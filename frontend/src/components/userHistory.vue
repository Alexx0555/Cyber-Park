<template>
  <div class="maincont">
    <header class="allhead">
      <h1>📜 Your Personal Parking Chronicle 📜</h1>
      <p>A record of your tributes and travels.</p>
      <div class="user-info">
        <div class="nav-buttons">
          <button @click="goback" class="btn-secondary">← Back to Dashboard</button>
        </div>
        <div class="user-profile">
          <div class="profile-dropdown" @click="toglog_btn">
            <div class="profile-icon">
              <span>🧙‍♂️</span>
            </div>
            <div class="logout-dropdown" v-show="showlogout">
              <button @click="logout" class="btn-logout">🚪 Exit Warrior's Realm</button>
            </div>
          </div>
        </div>
      </div>
    </header>

    <section class="widget">
      <h2 class="widget-title">🚗 Your Parking History</h2>
      <div class="widget-content">
        <div v-if="loading" class="loading">
          <p>Loading your parking history...</p>
        </div>
        <div v-else-if="error" class="error">
          <p>{{ error }}</p>
          <button @click="fetuhist" class="btn-primary">Retry</button>
        </div>
        <div v-else-if="uhist.length === 0" class="no-data">
          <p>No parking history yet. Start parking to see your records here!</p>
        </div>
        <div v-else>
          <table class="hist-tab">
            <thead>
              <tr>
                <th>Location</th>
                <th>Spot</th>
                <th>Vehicle</th>
                <th>Start Time</th>
                <th>End Time</th>
                <th>Duration</th>
                <th>Price/Hour</th>
                <th>Total Cost</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="r in histpg" :key="r.id" :class="{ 'act-reserv': !r.leaving_timestamp }" >
                <td>{{ r.prime_location_name }}</td>
                <td>{{ r.spot_number || 'N/A' }}</td>
                <td>{{ r.vehicle_number }}</td>
                <td>{{ formatdt(r.parking_timestamp) }}</td>
                <td>{{ r.leaving_timestamp ? formatdt(r.leaving_timestamp) : 'Active' }}</td>
                <td>{{ calcdur(r) }}</td>
                <td>${{ getpricperhr(r).toFixed(2) }}</td>
                <td>${{ (r.parking_cost || 0).toFixed(2) }}</td>
                <td>
                  <span v-if="!r.leaving_timestamp" class="status-active">Active</span>
                  <span v-else class="status-completed">Completed</span>
                </td>
              </tr>
            </tbody>
          </table>

          <div class="pagination" v-if="totpgs > 1">
            <button  @click="currpg = Math.max(1, currpg - 1)" :disabled="currpg === 1" class="btn-secondary" >
              ← Previous
            </button>
            
            <span class="page-info">
              Page {{ currpg }} of {{ totpgs }}
            </span>
            
            <button  @click="currpg = Math.min(totpgs, currpg + 1)" :disabled="currpg === totpgs" class="btn-secondary" >
              Next →
            </button>
          </div>

          <div>
            <h3>📊 Summary</h3>
            <div class="summary-stats">
              <div class="summary-item">
                <div class="value">{{ uhist.length }}</div>
                <div class="label">Total Sessions</div>
              </div>
              <div class="summary-item">
                <div class="value">${{ totspent.toFixed(2) }}</div>
                <div class="label">Total Spent</div>
              </div>
              <div class="summary-item">
                <div class="value">{{ compsess }}</div>
                <div class="label">Completed</div>
              </div>
              <div class="summary-item">
                <div class="value">{{ activesess }}</div>
                <div class="label">Active</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>


  </div>
</template>

<script>
export default {
  name: 'userHistory',
  data() {
    return {
      uhist: [],
      parkinglots: [],
      loading: true,
      error: null,
      accessToken: localStorage.getItem('access_token'),
      showlogout: false,
      currpg: 1,
      itemperpg: 10
    };
  },
  async mounted() {
    if (!this.accessToken) {
      this.$router.push('/');
      return;
    }
    await this.fetchuplots();
    await this.fetuhist();
  },
  computed: {
    totspent() {
      return this.uhist.reduce((total, record) => total + (record.parking_cost || 0), 0);
    },

    compsess() {
      return this.uhist.filter(record => record.leaving_timestamp).length;
    },

    activesess() {
      return this.uhist.filter(record => !record.leaving_timestamp).length;
    },

    totpgs() {
      return Math.ceil(this.uhist.length / this.itemperpg);
    },

    histpg() {
      const start = (this.currpg - 1) * this.itemperpg;
      const end = start + this.itemperpg;
      return this.uhist.slice(start, end);
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

    async fetuhist() {
      try {
        this.loading = true;
        const resp = await this.makeauthreq('/api/user/reservations');  
        if (resp && resp.ok) {
          const data = await resp.json();
          this.uhist = data.reservations || [];
          this.uhist.sort((a, b) => new Date(b.parking_timestamp) - new Date(a.parking_timestamp));
          this.error = null;
        } 
        else {
          this.error = 'Failed to load parking history';
        }
      } 
      catch (error) {
        console.error('Error fetching user history:', error);
        this.error = 'Error loading parking history';
      } 
      finally {
        this.loading = false;
      }
    },

    async fetchuplots() {
      try {
        const resp = await this.makeauthreq('/api/user/parking-lots');
        if (resp && resp.ok) {
          const data = await resp.json();
          this.parkinglots = data.parking_lots || [];
        }
      } 
      catch (error) {
        console.error('Error fetching parking lots:', error);
      }
    },

    getpricperhr(rec) {
      const lot = this.parkinglots.find(l => l.name === rec.prime_location_name);
      return lot ? lot.price_per_hour : 5; 
    },

    formatdt(d) {
      return new Date(d).toLocaleString();
    },

    calcdur(rec) {
      const start = new Date(rec.parking_timestamp);
      const end = rec.leaving_timestamp ? new Date(rec.leaving_timestamp) : new Date();
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
      this.$router.push('/');
    },

    goback() {
      const urole = localStorage.getItem('user_role');
      if (urole === 'admin') {
        this.$router.push('/admin');
      } else {
        this.$router.push('/dashboard');
      }
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

.act-reserv {
  background-color: rgba(255, 165, 0, 0.1);
}
</style>
