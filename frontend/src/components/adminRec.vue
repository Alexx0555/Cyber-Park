<template>
  <div class="maincont">
    <header class="allhead">
      <h1>📊 The Sacred Archives of All Mortals 📊</h1>
      <p>Behold! The complete chronicles of all parking warriors!</p>
      <div class="user-info">
        <button @click="goback" class="btn-secondary">← Back to Admin Portal</button>
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
      </div>
    </header>

    <section class="widget">
      <h2 class="widget-title">🗂️ Complete User Records Database</h2>
      <div class="widget-content">
        <div v-if="loading" class="loading">
          <p>🔮 The Oracle is consulting the ancient scrolls...</p>
        </div>
        <div v-else-if="error" class="error">
          <p>💀 {{ error }}</p>
          <button @click="fetallrec" class="btn-primary">🔄 Retry Divination</button>
        </div>
        <div v-else-if="allrec.length === 0" class="no-data">
          <p>🌌 The void is empty... No records found in the cosmic database!</p>
        </div>
        <div v-else>
          <div class="records-stats">
            <div class="stat-card">
              <h3>{{ allrec.length }}</h3>
              <p>Total Records</p>
            </div>
            <div class="stat-card">
              <h3>{{ actrec }}</h3>
              <p>Active Sessions</p>
            </div>
            <div class="stat-card">
              <h3>{{ comprec }}</h3>
              <p>Completed Sessions</p>
            </div>
            <div class="stat-card">
              <h3>${{ totrev.toFixed(2) }}</h3>
              <p>Total Revenue</p>
            </div>
          </div>

          <div>
            <input type="text" v-model="searchq" placeholder="🔍 Search by user, location, or vehicle..." class="search-inp"/>
            <select v-model="filterStatus" class="filter-sel">
              <option value="">All Sessions</option>
              <option value="active">Active Sessions</option>
              <option value="completed">Completed Sessions</option>
            </select>
            <select v-model="filloc" class="filter-sel">
              <option value="">All Locations</option>
              <option v-for="loc in uniqloc" :key="loc" :value="loc">
                {{ loc }}
              </option>
            </select>
          </div>

          <div>
            <table class="records-table">
              <thead>
                <tr>
                  <th>👤 User</th>
                  <th>📍 Location</th>
                  <th>🅿️ Spot</th>
                  <th>🚗 Vehicle</th>
                  <th>📅 Booked At</th>
                  <th>⏰ Start Time</th>
                  <th>🏁 End Time</th>
                  <th>⏱️ Duration</th>
                  <th>💰 Cost</th>
                  <th>📊 Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="rec in paginatedrecords" :key="rec.id" class="record-row">
                  <td>
                    <div class="user-info-cell">
                      <strong>{{ rec.user_name }}</strong>
                    </div>
                  </td>
                  <td>{{ rec.prime_location_name }}</td>
                  <td>{{ rec.spot_number }}</td>
                  <td>{{ rec.vehicle_number }}</td>
                  <td>
                    <span v-if="rec.booking_timestamp">{{ formatdt(rec.booking_timestamp) }}</span>
                    <span v-else class="no-data">-</span>
                  </td>
                  <td>{{ formatdt(rec.start_time) }}</td>
                  <td>
                    <span v-if="rec.end_time">{{ formatdt(rec.end_time) }}</span>
                    <span v-else class="active-session">🔴 Active</span>
                  </td>
                  <td>{{ calcdur(rec) }}</td>
                  <td>
                    <span class="amt">${{ (rec.cost || 0).toFixed(2) }}</span>
                  </td>
                  <td>
                    <span v-if="rec.end_time" class="status-completed">✅ Completed</span>
                    <span v-else class="status-active">🔴 Active</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="pagination" v-if="totpgs > 1">
            <button @click="currpg = Math.max(1, currpg - 1)" :disabled="currpg === 1" class="btn-secondary">
              ← Previous
            </button>
            
            <span class="page-info">
              Page {{ currpg }} of {{ totpgs }}
            </span>
            
            <button @click="currpg = Math.min(totpgs, currpg + 1)" :disabled="currpg === totpgs" class="btn-secondary">
              Next →
            </button>
          </div>
        </div>
      </div>
    </section>
    
  </div>
</template>

<script>
import { showToast } from '../utils/toast.js'

export default {
  name: 'adminRec',
  data() {
    return {
      allrec: [],
      loading: true,
      error: null,
      accessToken: localStorage.getItem('access_token'),
      showlogout: false,
      logouttimer: null,
      searchq: '',
      filterStatus: '',
      filloc: '',
      currpg: 1,
      itemperpg: 15
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

    await this.fetallrec();
  },
  computed: {
    actrec() {
      return this.allrec.filter(rec => !rec.end_time).length;
    },

    comprec() {
      return this.allrec.filter(rec => rec.end_time).length;
    },

    totrev() {
      return this.allrec.reduce((total, rec) => total + (rec.cost || 0), 0);
    },

    uniqloc() {
      const locs = [...new Set(this.allrec.map(rec => rec.prime_location_name))];
      return locs.sort();
    },

    filteredrec() {
      let filtered = this.allrec;

      if (this.searchq) {
        const query = this.searchq.toLowerCase();
        filtered = filtered.filter(rec => 
          rec.user_name.toLowerCase().includes(query) || rec.location.toLowerCase().includes(query) ||
          rec.vehicle_number.toLowerCase().includes(query) || rec.spot_number.toLowerCase().includes(query));
      }

      if (this.filterStatus === 'active') {
        filtered = filtered.filter(rec => !rec.end_time);
      } 
      else if (this.filterStatus === 'completed') {
        filtered = filtered.filter(rec => rec.end_time);
      }

      if (this.filloc) {
        filtered = filtered.filter(rec => rec.location === this.filloc);
      }

      return filtered;
    },

    paginatedrecords() {
      const start = (this.currpg - 1) * this.itemperpg;
      const end = start + this.itemperpg;
      return this.filteredrec.slice(start, end);
    },

    totpgs() {
      return Math.ceil(this.filteredrec.length / this.itemperpg);
    }
  },
  watch: {
    searchq() {
      this.currpg = 1;
    },
    filterStatus() {
      this.currpg = 1;
    },
    filloc() {
      this.currpg = 1;
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

    async fetallrec() {
      try {
        this.loading = true;
        this.error = null;
        const resp = await this.makeauthreq('/api/admin/parking-records');
        if (resp && resp.ok) {
          const data = await resp.json();
          this.allrec = data.records || [];
          this.allrec.sort((a, b) => new Date(b.start_time) - new Date(a.start_time));
        } 
        else {
          this.error = 'Failed to load records';
        }
      } 
      catch (error) {
        console.error('Error fetching records:', error);
        this.error = 'Error loading records';
      } 
      finally {
        this.loading = false;
      }
    },

    formatdt(d) {
      if (!d) return 'N/A';
      return new Date(d).toLocaleString();
    },

    calcdur(rec) {
      const start = new Date(rec.start_time);
      const end = rec.end_time ? new Date(rec.end_time) : new Date();
      const dtot = end - start;
      const dhr = Math.floor(dtot / (1000 * 60 * 60));
      const dmins = Math.floor((dtot % (1000 * 60 * 60)) / (1000 * 60));
      return `${dhr}h ${dmins}m`;
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

    goback() {
      this.$router.push('/admin');
    },
  }
}
</script>

<style scoped>
.status-active {
  color: #ffa500;
  font-weight: bold;
}

.status-completed {
  color: #00ff00;
  font-weight: bold;
}

.active-session {
  color: #ff4444;
  font-weight: bold;
}

.amt {
  font-weight: bold;
  color: #4ecdc4;
}

.user-info-cell {
  display: flex;
  flex-direction: column;
}

.booking-status-cancelled {
  color: #ff4757;
  font-weight: bold;
}

.booking-status-auto-cancelled {
  color: #ff6b35;
  font-weight: bold;
}

.booking-status-occupied {
  color: #2ed573;
  font-weight: bold;
}

.booking-status-booked {
  color: #3742fa;
  font-weight: bold;
}

.booking-status-legacy {
  color: #747d8c;
  font-style: italic;
}

.no-data {
  color: #a4b0be;
  font-style: italic;
}


</style>
