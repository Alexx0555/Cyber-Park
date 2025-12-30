<template>
  <div class="maincont">
    <header class="allhead">
      <h1>👥 The Registry of All Parking Warriors 👥</h1>
      <p>Manage the mortals who dare to park in our sacred grounds!</p>
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
      <h2 class="widget-title">🧙‍♂️ User Management Console</h2>
      <div class="widget-content">
        <div v-if="loading" class="loading">
          <p>🔮 Summoning the list of all parking warriors...</p>
        </div>
        <div v-else-if="error" class="error">
          <p>💀 {{ error }}</p>
          <button @click="fetusers" class="btn-primary">🔄 Retry Summoning</button>
        </div>
        <div v-else-if="users.length === 0" class="no-data">
          <p>🌌 The realm is empty... No warriors have joined our cause!</p>
        </div>
        <div v-else>
          <div class="users-stats">
            <div class="stat-card">
              <h3>{{ users.length }}</h3>
              <p>Total Warriors</p>
            </div>
          </div>

          <div>
            <input type="text" v-model="searchq" placeholder="🔍 Search warriors by name or email..." class="search-inp">
          </div>

          <div>
            <table class="users-table">
              <thead>
                <tr>
                  <th>👤 Warrior</th>
                  <th>📧 Contact</th>
                  <th>📱 Phone</th>
                  <th>⭐ Loyalty Points</th>
                  <th>📅 Joined</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="u in filusers" :key="u.id">
                  <td>
                    <div class="user-info-cell">
                      <strong>{{ u.username }}</strong>
                    </div>
                  </td>
                  <td>{{ u.email }}</td>
                  <td>{{ u.phone_number }}</td>
                  <td>
                    <span class="loyalty-points">{{ u.loyalty_points}}</span>
                  </td>
                  <td>{{ formatdt(u.profile_created_at) }}</td>
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
  name: 'adminUsers',
  data() {
    return {
      users: [],
      loading: true,
      error: null,
      accessToken: localStorage.getItem('access_token'),
      showlogout: false,
      logouttimer: null,
      searchq: '',
      currpg: 1,
      itemperpg: 10,
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

    await this.fetusers();
  },
  computed: {
    filusers() {
      let filtered = this.users;

      if (this.searchq) {
        const query = this.searchq.toLowerCase();
        filtered = filtered.filter(user => 
          user.username.toLowerCase().includes(query) ||(user.email && user.email.toLowerCase().includes(query)));
      }
      const start = (this.currpg - 1) * this.itemperpg;
      const end = start + this.itemperpg;
      return filtered.slice(start, end);
    },

    totpgs() {
      let filtered = this.users;
      if (this.searchq) {
        const query = this.searchq.toLowerCase();
        filtered = filtered.filter(user => 
          user.username.toLowerCase().includes(query) || (user.email && user.email.toLowerCase().includes(query)) );
      }
      return Math.ceil(filtered.length / this.itemperpg);
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

    async fetusers() {
      try { 
        this.loading = true;
        this.error = null;
        const resp = await this.makeauthreq('/api/admin/users');

        if (resp && resp.ok) {
          const data = await resp.json();
          this.users = data.users || [];
        }
        else {
          this.error = 'Failed to load users';
        }
      } 
      catch (error) {
        console.error('Error fetching users:', error);
        this.error = 'Error loading users';
      }
       finally {
        this.loading = false;
      }
    },

    formatdt(d) {
      if (!d) return 'N/A';
      return new Date(d).toLocaleDateString();
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
    }
  }
}
</script>

<style scoped>
.btn-small {
  padding: 4px 8px;
  font-size: 0.8em;
  margin: 0 2px;
}

.user-info-cell {
  display: flex;
  flex-direction: column;
}

.user-id {
  font-size: 0.8em;
  color: #666;
}

.loyalty-points {
  font-weight: bold;
  color: #ffa500;
}
</style>