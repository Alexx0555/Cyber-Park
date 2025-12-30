<template>
  <div class="maincont">
    <header class="allhead">
      <h1>🔮 All-Seeing Oracle's Dashboard 🔮</h1>
      <p>Gaze upon the sacred parking grounds...</p>
      <div class="admin-profile">
        <div class="profile-dropdown">
          <div class="profile-icon" @click="toglog_btn">
            <span>👑</span>
          </div>
          <div class="logout-dropdown" v-show="showlogout">
            <button @click="logout" class="btn-logout">🚪 Exit Oracle's Realm</button>
          </div>
        </div>
      </div>
    </header>

    <section class="widget">
      <h2 class="widget-title">🎛️ Supreme Oracle's Command Center</h2>
      <div class="widget-content">
        <div class="admin-actions">
          <button @click="gotousers" class="btn-primary">👥 Manage All Warriors</button>
          <button @click="gotorec" class="btn-primary">📊 View Sacred Archives</button>
          <button @click="gotofb" class="btn-primary">🎭 Cosmic Feedback</button>
        </div>
      </div>
    </section>

    <section class="widget">
      <h2 class="widget-title">🔮 Task Management Oracle</h2>
      <div class="widget-content">
        <div class="task-management-grid">
          <div class="task-card">
            <h3>📊 Data Export</h3>
            <p>Generate and export parking data</p>
            <button @click="exportallusers()" class="btn-primary">Export All Users</button>
          </div>

          <div class="task-card">
            <h3>📧 Email Reports</h3>
            <p>Send monthly reports to users</p>
            <button @click="sendmonthlyreports()" class="btn-primary">Send Monthly Reports</button>
          </div>
        </div>
      </div>
    </section>

    <section class="widget">
      <h2 class="widget-title">🏢 Sacred Grounds Management</h2>
      <div class="widget-content">
        <div class="section-header">
          <button @click="openlotmodal()" class="btn-primary">➕ Add New Sacred Ground</button>
        </div>
        
        <div v-if="parkinglots.length === 0" class="no-data">
          <p>No parking lots configured yet.</p>
        </div>
        
        <ul class="item-list" v-else>
          <li v-for="lot in parkinglots" :key="lot.id">
            <div class="item-info">
              <span><strong>{{ lot.name }}</strong></span>
              <p class="item-subtext">{{ lot.address }}</p>
              <p class="item-subtext">PIN: {{ lot.pin_code }}</p>
              <p class="item-subtext">Price: ${{ lot.price_per_hour }}/hour</p>
              <p class="item-subtext">Capacity: {{ lot.capacity }} spots</p>
              <p class="item-subtext" :class="{'status-ok': lot.available > 0, 'status-full': lot.available === 0}">
                Available: {{ lot.available }} / {{ lot.capacity }}
              </p>
            </div>
            <div class="item-actions">
              <button @click="editlot(lot)" class="btn-secondary">✏️ Edit</button>
              <button @click="viewlotspots(lot)" class="btn-secondary">🅿️ View Spots</button>
              <button @click="dellot(lot.id)" class="btn-danger">🗑️ Delete</button>
            </div>
          </li>
        </ul>
      </div>
    </section>


    <section class="widget" v-if="selectedlot">
      <h2 class="widget-title">🅿️ {{ selectedlot.name }} Layout</h2>
      <div class="widget-content">
        <div class="lot-layout">
          <div class="entrance">🚗 ENTRANCE 🚗
          </div>

          <div class="parking-rows">
            <div v-for="(row, rowind) in parkingrows" :key="rowind" class="parking-row">
              <div class="row-label">Row {{ rowind + 1 }}</div>
                <div class="spots-cont">
                  <div v-for="spot in row" :key="spot.id" class="parking-spot" :class="getspotcls(spot)" @click="selspot(spot)">
                    <div class="spot-number">{{ spot.spot_number }}</div>
                    <div class="spot-icon">{{ getspoticon(spot) }}</div>
                    <div v-if="spot.vehicle_type" class="vehicle-type">{{ spot.vehicle_type }}</div>
                    <div v-if="spot.is_occupied" class="vehicle-info">{{ spot.vehicle_number }}</div>
                </div>
              </div>
            </div>
          </div>
          <div class="parking-exit">🚪 EXIT 🚪
          </div>
        </div>
      </div>
    </section>

    <section class="widget">
      <h2 class="widget-title">📈 Sacred Analytics</h2>
      <div class="widget-content">
        <div v-if="allparkingrec.length === 0" class="no-data">
          <p>No parking history available to display charts.</p>
        </div>
        <div v-else class="charts-cont">
          <div class="chart-item">
            <h3>Monthly Revenue</h3>
            <canvas id="revenuechart" width="400" height="200"></canvas>
          </div>
          <div class="chart-item">
            <h3>Lot Usage</h3>
            <canvas id="lotusagechart" width="400" height="200"></canvas>
          </div>
        </div>
      </div>
    </section>

    <div v-if="showlotmodal" class="modal-overlay" @click="cllotmodal">
      <div class="modal-content" @click.stop>
        <h3>{{ iseditinglot ? '✏️ Edit Sacred Ground' : '➕ Add New Sacred Ground' }}</h3>
        <form @submit.prevent="savelot">
          <div class="form-group">
            <label for="lot-name">Name:</label>
            <input type="text" id="lot-name" v-model="currlot.name" :class="{ 'input-error': lotErrors.includes('name') }" required>
          </div>
          <div class="form-group">
            <label for="lot-addr">Address:</label>
            <input type="text" id="lot-addr" v-model="currlot.address"
              :class="{ 'input-error': lotErrors.includes('address') }"required>
          </div>
          <div class="form-group">
            <label for="lot-pin">PIN Code:</label>
            <input type="text" id="lot-pin" v-model="currlot.pin_code" 
              :class="{ 'input-error': lotErrors.includes('pin_code') }" required>
          </div>
          <div class="form-group">
            <label for="lot-price">Price per Hour ($):</label>
            <input type="number" id="lot-price" v-model="currlot.price_per_hour" step="0.01" min="0" required >
          </div>
          <div class="form-group">
            <label for="lot-capacity">Capacity:</label>
            <input type="number" id="lot-capacity" v-model="currlot.capacity" min="1" required>
          </div>
          
          <div v-if="lotErrors.length > 0" class="error-msgs">
            <ul>
              <li v-for="error in lotErrors" :key="error">{{ error }}</li>
            </ul>
          </div>
          
          <div class="modal-actions">
            <button type="submit" :disabled="issubmittinglot" class="btn-primary">
              {{ issubmittinglot ? '⏳ Saving...' : '💾 Save' }}
            </button>
            <button type="button" @click="cllotmodal" class="btn-secondary">❌ Cancel</button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="showspotmodal" class="modal-overlay" @click="clspotmodal">
      <div class="modal-content" @click.stop>
        <h3>🅿️ Spot Details</h3>
        <div v-if="selectedspot">
          <p><strong>Spot Number:</strong> {{ selectedspot.spot_number }}</p>
          <p><strong>Vehicle Type:</strong> {{ selectedspot.vehicle_type || 'Regular' }}</p>
          <p><strong>Status:</strong> 
            <span v-if="selectedspot.is_maintenance">🔧 Maintenance</span>
            <span v-else-if="selectedspot.is_occupied">🚗 Occupied</span>
            <span v-else>✅ Available</span>
          </p>
          <div v-if="selectedspot.is_occupied">
            <p><strong>Vehicle:</strong> {{ selectedspot.vehicle_number }}</p>
            <p><strong>User:</strong> {{ selectedspot.user_name }}</p>
            <p><strong>Since:</strong> {{ formatdt(selectedspot.parking_timestamp) }}</p>
          </div>
          <div v-else-if="selectedspot.status === 'B'">
            <div class="booked-spot-info">
              <p class="info-text">📅 This spot is currently booked by a user.</p>
              <p><strong>User:</strong> {{ selectedspot.user_name }}</p>
              <p><strong>Vehicle:</strong> {{ selectedspot.vehicle_number }}</p>
              <p><strong>Booked:</strong> {{ formatdt(selectedspot.booking_timestamp) }}</p>
              <p class="info-text">🚫 Maintenance and vehicle type changes are disabled for booked spots.</p>
            </div>
          </div>
          <div v-else-if="!selectedspot.is_occupied && selectedspot.status !== 'B'" class="spot-controls">
            <button @click="togmaintenance(selectedspot)" class="btn-secondary">
              {{ selectedspot.is_maintenance ? '✅ Mark Available' : '🔧 Mark Maintenance' }}
            </button>
            <button @click="togvehtype(selectedspot)" class="btn-primary">
              {{ selectedspot.vehicle_type === 'EV' ? '🔌➡️🚗 Switch to Non-EV' : '🚗➡️🔌 Switch to EV' }}
            </button>
          </div>
        </div>
        <div class="modal-actions">
          <button @click="clspotmodal" class="btn-primary">👍 Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { showToast } from '../utils/toast.js'

export default {
  name: 'admindash',
  data() {
    return {
      parkinglots: [],
      users: [],
      selectedlot: null,
      spots: [],
      showlotmodal: false,
      showspotmodal: false,
      iseditinglot: false,
      currlot: {
        id: null,
        name: '',
        address: 'tamilnadu',
        pin_code: '123456',
        price_per_hour: 50.00,
        capacity: 10
      },
      lotErrors: [],
      issubmittinglot: false,
      showlogout: false,
      logouttimer: null,
      accessToken: localStorage.getItem('access_token'),
      allparkingrec: [],
      revenuechartinst: null,
      lotusageinst: null,
      selectedspot: null,
    };
  },
  async mounted() {
    if (!this.accessToken) {
      this.$router.push('/');
      return;
    }

    const urole = localStorage.getItem('user_role');
    if (urole !== 'admin') {
      showToast.error('Access denied. Admin privileges required.');
      this.$router.push('/dashboard');
      return;
    }

    await this.loadparkinglots();
    await this.loadusers();
    await this.loadallparkingrec();

    setTimeout(() => {this.createcharts();}, 1000);
  },

  computed: {
    parkingrows() {
      if (!this.spots.length) return [];
      const spotsperrow = 5;
      const rows = [];
      const sortspots = [...this.spots].sort((a, b) => {
        const n1 = parseInt(a.spot_number, 10) || 0;
        const n2 = parseInt(b.spot_number, 10) || 0;
        return n1 - n2;
      });

      for (let i = 0; i < sortspots.length; i += spotsperrow) {
        const row = sortspots.slice(i, i + spotsperrow);
        rows.push(row);
      }
      return rows;
    }
  },
  methods: {
    async makeauthreq(url, options = {}) {
      const headers = {
        'Authorization': `Bearer ${this.accessToken}`,
        'Content-Type': 'application/json',
        ...options.headers
      };

      const resp = await fetch(url, {
        ...options,
        headers
      });

      if (resp.status === 401) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        this.$router.push('/');
        return null;
      }

      return resp;
    },

    async loadparkinglots() {
      try {
        const resp = await this.makeauthreq('/api/admin/parking-lots');
        if (resp && resp.ok) {
          const data = await resp.json();
          this.parkinglots = data.parking_lots || [];
        }
      } 
      catch (error) {
        console.error('Error loading parking lots:', error);
      }
    },

    async loadusers() {
      try {
        const resp = await this.makeauthreq('/api/admin/users');
        if (resp && resp.ok) {
          const data = await resp.json();
          this.users = data.users || [];
        }
      } catch (error) {
        console.error('Error loading users:', error);
      }
    },

    async loadallparkingrec() {
      try {
        const resp = await this.makeauthreq('/api/admin/parking-records');
        if (resp && resp.ok) {
          const data = await resp.json();
          this.allparkingrec = data.records || [];
        }
      }
       catch (error) {
        console.error('Error loading parking records:', error);
      }
    },

    async viewlotspots(lot) {
      this.selectedlot = lot;
      try {
        const resp = await this.makeauthreq(`/api/admin/parking-lots/${lot.id}/spots`);
        if (resp && resp.ok) {
          const data = await resp.json();
          this.spots = data.spots || [];
        }
      } 
      catch (error) {
        console.error('Error loading spots:', error);
      }
    },

    openlotmodal() {
      this.iseditinglot = false;
      this.currlot = {
        id: null,
        name: '',
        address: 'tamilnadu',
        pin_code: '123456',
        price_per_hour: 50.00,
        capacity: 10
      };
      this.lotErrors = [];
      this.showlotmodal = true;
    },

    editlot(lot) {
      this.iseditinglot = true;
      this.currlot = { ...lot };
      this.lotErrors = [];
      this.showlotmodal = true;
    },

    cllotmodal() {
      this.showlotmodal = false;
      this.currlot = {
        id: null,
        name: '',
        address: '',
        pin_code: '',
        price_per_hour: 50.00,
        capacity: 10
      };
      this.lotErrors = [];
    },

    async savelot() {
      this.lotErrors = [];
      this.issubmittinglot = true;

      if (!this.currlot.name.trim()) {
        this.lotErrors.push('Name is required');
      }
      if (!this.currlot.address.trim()) {
        this.lotErrors.push('Address is required');
      }
      if (!this.currlot.pin_code.trim()) {
        this.lotErrors.push('PIN code is required');
      }

      if (this.lotErrors.length > 0) {
        this.issubmittinglot = false;
        return;
      }

      try {
        const url = this.iseditinglot? `/api/admin/parking-lots/${this.currlot.id}`: '/api/admin/parking-lots';
        const method = this.iseditinglot ? 'PUT' : 'POST';

        const resp = await this.makeauthreq(url, {
          method: method,
          body: JSON.stringify(this.currlot)
        });

        if (resp && resp.ok) {
          alert(`✅ Parking lot ${this.iseditinglot ? 'updated' : 'created'} successfully!`);
          this.cllotmodal();
          await this.loadparkinglots();
        } 
        else if (resp) {
          const data = await resp.json();
          alert(`❌ Error: ${data.message || 'Failed to save parking lot'}`);
        }
      }
       catch (error) {
        console.error('Error saving parking lot:', error);
        alert('❌ Error saving parking lot');
      } 
      finally {
        this.issubmittinglot = false;
      }
    },

    async dellot(lotid) {
      if (!confirm('Are you sure you want to delete this parking lot? This action cannot be undone.')) {
        return;
      }

      try {
        const resp = await this.makeauthreq(`/api/admin/parking-lots/${lotid}`, {
          method: 'DELETE'
        });

        if (resp && resp.ok) {
          alert('✅ Parking lot deleted successfully!');
          await this.loadparkinglots();
          if (this.selectedlot && this.selectedlot.id === lotid) {
            this.selectedlot = null;
            this.spots = [];
          }
        } 
        else if (resp) {
          const data = await resp.json();
          alert(`❌ Error: ${data.message || 'Failed to delete parking lot'}`);
        }
      } 
      catch (error) {
        console.error('Error deleting parking lot:', error);
        alert('❌ Error deleting parking lot');
      }
    },

    getspotcls(spot) {
      const classes = ['parking-spot'];

      if (spot.is_occupied) {
        classes.push('occupied');
      } 
      else if (spot.is_maintenance) {
        classes.push('maintenance');
      } 
      else if (spot.status === 'B' || spot.is_booked) {
        classes.push('booked');
      } 
      else {
        classes.push('available');
        if (spot.vehicle_type === 'EV') {
          classes.push('ev-spot');
        }
      }
      return classes;
    },

    getspoticon(spot) {
      if (spot.is_maintenance) return '🔧';
      if (spot.is_occupied) return '🚗';
      if (spot.status === 'B' || spot.is_booked) return '📅'; 
      if (spot.vehicle_type === 'EV') return '⚡';
      return '🅿️';
    },

    selspot(spot) {
      this.selectedspot = spot;
      this.showspotmodal = true;
    },

    clspotmodal() {
      this.showspotmodal = false;
      this.selectedspot = null;
    },

    async togmaintenance(spot) {
      try {
        let reqdata;
        if (spot.is_maintenance) {
          reqdata = {
            is_under_maintenance: false
          };
        }
         else {
          const reason = prompt('Please enter maintenance reason:');
          if (!reason || !reason.trim()) {
            alert('❌ Maintenance reason is required');
            return;
          }
          reqdata = {
            is_under_maintenance: true,
            maintenance_reason: reason.trim()
          };
        }

        const resp = await this.makeauthreq(`/api/admin/parking-spots/${spot.id}/maintenance`, {
          method: 'PUT',
          body: JSON.stringify(reqdata)
        });

        if (resp && resp.ok) {
          const data = await resp.json();
          alert(`✅ ${data.message}`);
          this.clspotmodal();
          await this.viewlotspots(this.selectedlot);
        } 
        else if (resp) {
          const data = await resp.json();
          alert(`❌ Error: ${data.message || 'Failed to update spot'}`);
        }
      } 
      catch (error) {
        console.error('Error updating spot:', error);
        alert('❌ Error updating spot');
      }
    },

    async togvehtype(spot) {
      try {
        const newtype = spot.vehicle_type === 'EV' ? 'non-EV' : 'EV';

        const resp = await this.makeauthreq(`/api/admin/parking-spots/${spot.id}/vehicle-type`, {
          method: 'PUT',
          body: JSON.stringify({
            vehicle_type: newtype
          })
        });

        if (resp && resp.ok) {
          const data = await resp.json();
          alert(`✅ ${data.message}`);
          this.clspotmodal();
          await this.viewlotspots(this.selectedlot);
        } 
        else if (resp) {
          const data = await resp.json();
          alert(`❌ Error: ${data.message || 'Failed to update vehicle type'}`);
        }
      } 
      catch (error) {
        console.error('Error updating vehicle type:', error);
        alert('❌ Error updating vehicle type');
      }
    },

    formatdt(d) {
      try {
        const date = new Date(d);
        if (isNaN(date.getTime())) {
          return 'Invalid Date';
        }
        return date.toLocaleString('en-US', {
          year: 'numeric',
          month: 'short',
          day: 'numeric',
          hour: 'numeric',
          minute: 'numeric',
          second: 'numeric',
        });
      }
       catch (error) {
        console.error('Error formatting date:', error);
        return 'Invalid Date';
      }
    },

    toglog_btn() {
      this.showlogout = !this.showlogout;
      if (this.logouttimer) {
        clearTimeout(this.logouttimer);
        this.logouttimer = null;
      }
      if (this.showlogout) {
        this.logouttimer = setTimeout(() => {
          this.showlogout = false;
          this.logouttimer = null;
        }, 3000);
      }
    },

    logout() {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_role');
      showToast.logoutSuccess();
      this.$router.push('/');
    },

    toggleTheme() {
      this.isDarkMode = !this.isDarkMode;
      localStorage.setItem('admin-theme', this.isDarkMode ? 'dark' : 'light');
      document.body.style.backgroundColor = this.isDarkMode ? '#0a0a0a' : '#ffffff';
    },

    gotousers() {
      this.$router.push('/admin/users');
    },

    gotorec() {
      this.$router.push('/admin/records');
    },

    gotofb() {
      this.$router.push('/admin/feedback');
    },

    async exportallusers() {
      try {
        const resp = await this.makeauthreq('/api/admin/export-users', {
          method: 'POST'
        });

        if (resp && resp.ok) {
          showToast.adminAction('User export', 'initiated! You will receive an email with the CSV file');
        }
        else if (resp) {
          const data = await resp.json();
          showToast.adminError(data.message || 'Failed to export users');
        }
      }
      catch (error) {
        console.error('Error exporting users:', error);
        showToast.adminError('Error exporting users');
      }
    },

    async sendmonthlyreports() {
      try {
        const resp = await this.makeauthreq('/api/admin/send-monthly-reports', {
          method: 'POST'
        });

        if (resp && resp.ok) {
          showToast.adminAction('Monthly reports', 'initiated! Users will receive their reports via email');
        }
        else if (resp) {
          const data = await resp.json();
          showToast.adminError(data.message || 'Failed to send reports');
        }
      }
      catch (error) {
        console.error('Error sending reports:', error);
        showToast.adminError('Error sending reports');
      }
    },

    createcharts() {
      try {
        this.createrevenuechart();
        this.createlotusagechart();
      } catch (error) {
        console.error('Error creating charts:', error);
      }
    },

    createrevenuechart() {
      const ctx = document.getElementById('revenuechart');
      if (ctx && this.allparkingrec.length > 0) {
        const monthlyrevenue = this.procmonthlyrevenue();

        if (this.revenuechartinst) {
          this.revenuechartinst.destroy();
        }

        this.revenuechartinst = new Chart(ctx, {
          type: 'line',
          data: {
            labels: monthlyrevenue.labels,
            datasets: [{
              label: 'Revenue ($)',
              data: monthlyrevenue.data,
              borderColor: '#ff6b6b',
              backgroundColor: 'rgba(255, 107, 107, 0.1)',
              tension: 0.4
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                display: false
              }
            },
            scales: {
              y: {
                beginAtZero: true,
                ticks: {
                  callback: function(value) {
                    return '$' + value;
                  }
                }
              }
            }
          }
        });
      }
    },

    createlotusagechart() {
      const ctx = document.getElementById('lotusagechart');
      if (ctx && this.allparkingrec.length > 0) {
        const lotusage = this.proclotusage();

        if (this.lotusageinst) {
          this.lotusageinst.destroy();
        }

        this.lotusageinst = new Chart(ctx, {
          type: 'doughnut',
          data: {
            labels: lotusage.labels,
            datasets: [{
              data: lotusage.data,
              backgroundColor: [
                '#ff6b6b',
                '#4ecdc4',
                '#45b7aa',
                '#96ceb4',
                '#feca57',
                '#ff9ff3',
                '#54a0ff'
              ]
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                position: 'bottom'
              }
            }
          }
        });
      }
    },

    procmonthlyrevenue() {
      const monthlystats = {};
      const now = new Date();

      for (let i = 5; i >= 0; i--) {
        const date = new Date(now.getFullYear(), now.getMonth() - i, 1);
        const key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
        monthlystats[key] = 0;
      }

      this.allparkingrec.forEach(record => {
        if (record.cost) {
          const date = new Date(record.start_time);
          const key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;

          if (monthlystats.hasOwnProperty(key)) {
            monthlystats[key] += record.cost;
          }
        }
      });

      const labels = Object.keys(monthlystats).map(key => {
        const [year, month] = key.split('-');
        const date = new Date(year, month - 1);
        return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
      });

      return {
        labels: labels,
        data: Object.values(monthlystats)
      };
    },

    proclotusage() {
      const lotusage = {};

      this.allparkingrec.forEach(record => {
        const lotname = record.prime_location_name;
        if (lotusage[lotname]) {
          lotusage[lotname]++;
        } else {
          lotusage[lotname] = 1;
        }
      });

      return {
        labels: Object.keys(lotusage),
        data: Object.values(lotusage)
      };
    },
  }
}
</script>

<style scoped>
.task-management-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.task-card {
  background: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #ddd;
}

.task-card h3 {
  margin-top: 0;
  color: #333;
}

.task-card p {
  color: #666;
  margin-bottom: 15px;
}

.charts-cont {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.chart-item {
  background: #f9f9f9;
  padding: 15px;
  border-radius: 8px;
  border: 1px solid #ddd;
  height: 300px;
}

.chart-item h3 {
  margin-top: 0;
  margin-bottom: 15px;
  text-align: center;
}

.chart-item canvas {
  max-height: 250px !important;
}

.spot-controls {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.spot-controls button {
  width: 100%;
}

.no-data {
  text-align: center;
  padding: 20px;
  font-style: italic;
  color: #888;
}
</style>