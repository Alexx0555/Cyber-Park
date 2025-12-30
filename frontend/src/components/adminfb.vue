<template>
  <div class="maincont">
    <header class="allhead">
      <h1>🎭 Cosmic Feedback Oracle 🎭</h1>
      <p>Divine wisdom from the mortal realm...</p>
      <div class="user-info">
        <button @click="goback" class="btn-secondary">← Back to Oracle's Realm</button>
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

    <main class="dashboard-main">
      <section class="widget">
        <h2 class="widget-title">📊 Cosmic Feedback Statistics</h2>
        <div class="widget-content">
          <div class="stats-grid">
            <div class="stat-card">
              <div class="stat-number">{{ fbstats.total }}</div>
              <div class="stat-label">Total Feedback</div>
            </div>
            <div class="stat-card">
              <div class="stat-number">{{ fbstats.open }}</div>
              <div class="stat-label">Open Issues</div>
            </div>
            <div class="stat-card">
              <div class="stat-number">{{ fbstats.inProgress }}</div>
              <div class="stat-label">In Progress</div>
            </div>
            <div class="stat-card">
              <div class="stat-number">{{ fbstats.resolved }}</div>
              <div class="stat-label">Resolved</div>
            </div>
          </div>
        </div>
      </section>

      <section class="widget">
        <h2 class="widget-title">🗂️ Feedback Management Console</h2>
        <div class="widget-content">
          <div v-if="loading" class="loading">
            <p>🔮 Channeling cosmic feedback...</p>
          </div>
          <div v-else-if="error" class="error">
            <p>💀 {{ error }}</p>
            <button @click="fetallfb" class="btn-primary">🔄 Retry Channeling</button>
          </div>
          <div v-else-if="allfb.length === 0" class="no-data">
            <p>🌌 The cosmic void is silent... No feedback received yet!</p>
          </div>
          <div v-else>
            <div>
              <select v-model="statusfilt" class="filter-sel">
                <option value="">All Status</option>
                <option value="Open">Open</option>
                <option value="In Progress">In Progress</option>
                <option value="Resolved">Resolved</option>
                <option value="Closed">Closed</option>
              </select>
              
              <select v-model="catfilt" class="filter-sel">
                <option value="">All Categories</option>
                <option v-for="cat in uniqcat" :key="cat" :value="cat">
                  {{ cat }}
                </option>
              </select>
              
              <input 
                type="text" v-model="searchq" placeholder="🔍 Search feedback..." class="search-inp">
            </div>

            <div class="fb-list">
              <div v-for="fb in fbpgs" :key="fb.id" class="fb-item" :class="{ 'unread': fb.status === 'Open' }">
                <div class="fb-header">
                  <div class="fb-meta">
                    <span class="fb-id">#{{ fb.id }}</span>
                    <span class="fb-user">{{ fb.user_name }}</span>
                    <span class="fb-date">{{ formatdt(fb.submitted_at) }}</span>
                  </div>
                  <div class="fb-badges">
                    <span class="fb-cat">{{ fb.issue_category }}</span>
                    <span :class="statuscls(fb.status)">{{ fb.status }}</span>
                  </div>
                </div>
                
                <div class="fb-content">
                  <div v-if="fb.parking_lot_name" class="fb-location">
                    <strong>📍 Location:</strong> {{ fb.parking_lot_name }}
                    <span v-if="fb.spot_number" class="spot-info"> | 🅿️ Spot {{ fb.spot_number }}</span>
                  </div>
                  <div class="fb-desc">{{ fb.description }}</div>
                  
                  <div class="fb-contact">
                    <span><strong>Email:</strong> {{ fb.user_email || 'Not provided' }}</span>
                    <span><strong>Phone:</strong> {{ fb.user_phone || 'Not provided' }}</span>
                  </div>
                </div>
                
                <div v-if="fb.admin_response" class="admin-resp">
                  <h5>Admin Response:</h5>
                  <p>{{ fb.admin_response }}</p>
                  <div class="resp-date">{{ formatdt(fb.updated_at) }}</div>
                </div>
                
                <div class="fb-actions">
                  <button @click="openResponseModal(fb)" class="btn-primary">
                    {{ fb.admin_response ? '✏️ Edit Response' : '💬 Respond' }}
                  </button>
                  <select
                    :value="fb.status"
                    @change="updfbstatus(fb.id, $event.target.value)"
                    class="status-sel"
                >
                    <option value="Open">Open</option>
                    <option value="In Progress">In Progress</option>
                    <option value="Resolved">Resolved</option>
                    <option value="Closed">Closed</option>
                  </select>
                </div>
              </div>
            </div>

            <div class="pagination" v-if="totpgs > 1">
              <button 
                @click="currpg = Math.max(1, currpg - 1)"
                :disabled="currpg === 1"
                class="btn-secondary"
              >
                ← Previous
              </button>
              
              <span class="page-info">
                Page {{ currpg }} of {{ totpgs }}
              </span>
              
              <button 
                @click="currpg = Math.min(totpgs, currpg + 1)"
                :disabled="currpg === totpgs"
                class="btn-secondary"
              >
                Next →
              </button>
            </div>
          </div>
        </div>
      </section>
    </main>

    <div v-if="showrespmod" class="modal-overlay" @click="closerespmod">
      <div class="modal-content" @click.stop>
        <h3>💬 Respond to Feedback</h3>
        <div v-if="selfb">
          <div class="fb-summary">
            <p><strong>From:</strong> {{ selfb.user_name }}</p>
            <p><strong>Category:</strong> {{ selfb.issue_category }}</p>
            <p v-if="selfb.parking_lot_name"><strong>Location:</strong> {{ selfb.parking_lot_name }}</p>
            <p v-if="selfb.spot_number"><strong>Spot Number:</strong> {{ selfb.spot_number }}</p>
            <p><strong>Issue:</strong> {{ selfb.description }}</p>
          </div>
          
          <form @submit.prevent="subresp">
            <div class="form-group">
              <label for="admin-resp">Your Response:</label>
              <textarea  id="admin-resp" v-model="resptxt" rows="5" placeholder="Type your response to the user..." required ></textarea>
            </div>
            
            <div class="form-group">
              <label for="resp-status">Update Status:</label>
              <select id="resp-status" v-model="respstatus">
                <option value="Open">Open</option>
                <option value="In Progress">In Progress</option>
                <option value="Resolved">Resolved</option>
                <option value="Closed">Closed</option>
              </select>
            </div>
            
            <div class="modal-actions">
              <button type="submit" :disabled="submittingresp" class="btn-primary">
                {{ submittingresp ? '⏳ Sending...' : '📤 Send Response' }}
              </button>
              <button type="button" @click="closerespmod" class="btn-secondary">❌ Cancel</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'adminfb',
  data() {
    return {
      allfb: [],
      loading: true,
      error: null,
      accessToken: localStorage.getItem('access_token'),
      showlogout: false,
      logouttimer: null,
      statusfilt: '',
      catfilt: '',
      searchq: '',
      currpg: 1,
      itemperpg: 10,
      showrespmod: false,
      selfb: null,
      resptxt: '',
      respstatus: 'In Progress',
      submittingresp: false
    };
  },
  async mounted() {
    await this.checkauth();
    await this.fetallfb();
  },
  computed: {
    fbstats() {
      return {
        total: this.allfb.length,
        open: this.allfb.filter(f => f.status === 'Open').length,
        inProgress: this.allfb.filter(f => f.status === 'In Progress').length,
        resolved: this.allfb.filter(f => f.status === 'Resolved').length
      };
    },

    uniqcat() {
      const cats = [...new Set(this.allfb.map(f => f.issue_category))];
      return cats.sort();
    },

    filtfb() {
      let filtered = this.allfb;

      if (this.statusfilt) {
        filtered = filtered.filter(f => f.status === this.statusfilt);
      }

      if (this.catfilt) {
        filtered = filtered.filter(f => f.issue_category === this.catfilt);
      }

      if (this.searchq) {
        const query = this.searchq.toLowerCase();
        filtered = filtered.filter(f => 
          f.user_name.toLowerCase().includes(query) || f.description.toLowerCase().includes(query) ||
          (f.parking_lot_name && f.parking_lot_name.toLowerCase().includes(query)) ||
          (f.spot_number && f.spot_number.toLowerCase().includes(query)));
      }

      return filtered;
    },

    fbpgs() {
      const start = (this.currpg - 1) * this.itemperpg;
      const end = start + this.itemperpg;
      return this.filtfb.slice(start, end);
    },

    totpgs() {
      return Math.ceil(this.filtfb.length / this.itemperpg);
    }
  },
  watch: {
    statusfilt() {
      this.currpg = 1;
    },
    catfilt() {
      this.currpg = 1;
    },
    searchq() {
      this.currpg = 1;
    }
  },
  methods: {
    async checkauth() {
      const token = localStorage.getItem('access_token');
      if (!token) {
        this.$router.push('/');
        return;
      }

      const urole = localStorage.getItem('user_role');
      if (urole !== 'admin') {
        alert('Access denied. Admin privileges required.');
        this.$router.push('/dashboard');
        return;
      }
    },

    async makeauthreq(url, options = {}) {
      const token = localStorage.getItem('access_token');
      const defopt = {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      };

      const mergopt = {
        ...defopt,
        ...options,
        headers: {
          ...defopt.headers,
          ...options.headers
        }
      };

      const resp = await fetch(url, mergopt);

      if (resp.status === 401) {
        localStorage.removeItem('access_token');
        this.$router.push('/');
        return null;
      }

      return resp;
    },

    async fetallfb() {
      try {
        this.loading = true;
        this.error = null;
        const resp = await this.makeauthreq('/api/admin/feedback');

        if (resp && resp.ok) {
          const data = await resp.json();
          this.allfb = data.feedback || [];
          this.allfb.sort((a, b) => new Date(b.submitted_at) - new Date(a.submitted_at));
        } 
        else {
          this.error = 'Failed to load feedback';
        }
      } 
      catch (error) {
        console.error('Error fetching feedback:', error);
        this.error = 'Error loading feedback';
      } 
      finally {
        this.loading = false;
      }
    },

    async updfbstatus(fbid, newstat) {
      try {
        const resp = await this.makeauthreq(`/api/admin/feedback/${fbid}`, {
          method: 'PUT',
          body: JSON.stringify({ status: newstat })
        });

        if (resp && resp.ok) {
          const fb = this.allfb.find(f => f.id === fbid);
          if (fb) {
            fb.status = newstat;
            fb.updated_at = new Date().toISOString();
          }

          alert('✅ Status updated successfully!');
        } 
        else if (resp) {
          const data = await resp.json();
          alert(`❌ Error: ${data.message || 'Failed to update status'}`);
        }
      } 
      catch (error) {
        console.error('Error updating status:', error);
        alert('❌ Error updating status');
      }
    },

    openResponseModal(fb) {
      this.selfb = fb;
      this.resptxt = fb.admin_response || '';
      this.respstatus = fb.status;
      this.showrespmod = true;
    },

    closerespmod(){
      this.showrespmod=false;
      this.selfb=null;
      this.resptxt='';
      this.respstatus='In Progress';
    },

    async subresp() {
      if (!this.resptxt.trim()) {
        alert('Please enter a response');
        return;
      }

      try {
        this.submittingresp = true;
        const resp = await this.makeauthreq(`/api/admin/feedback/${this.selfb.id}`, {
          method: 'PUT',
          body: JSON.stringify({
            admin_response: this.resptxt,
            status: this.respstatus
          })
        });

        if (resp && resp.ok) {
          const fb = this.allfb.find(f => f.id === this.selfb.id);
          if (fb){
            fb.admin_response = this.resptxt;
            fb.status = this.respstatus;
            fb.updated_at = new Date().toISOString();
          }

          alert('✅ Response sent successfully!');
          this.closerespmod();
        } 
        else if (resp) {
          const data = await resp.json();
          alert(`❌ Error: ${data.message || 'Failed to send response'}`);
        }
      } 
      catch (error) {
        console.error('Error sending response:', error);
        alert('❌ Error sending response');
      } 
      finally {
        this.submittingresp = false;
      }
    },

    statuscls(s) {
      return {
        'fb-status': true,
        'open': s === 'Open',
        'in-progress': s === 'In Progress',
        'resolved': s === 'Resolved',
        'closed': s === 'Closed'
      };
    },

    formatdt(d) {
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
      this.$router.push('/');
    },

    goback() {
      this.$router.push('/admin');
    }
  }
}
</script>

<style scoped>
.fb-item {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;
  background: #fff;
}

.fb-item.unread {
  border-left: 4px solid #ff6b6b;
  background: #fff9f9;
}

.fb-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.fb-meta {
  display: flex;
  gap: 15px;
  align-items: center;
}

.fb-id {
  font-weight: bold;
  color: #666;
}

.fb-user {
  font-weight: bold;
  color: #333;
}

.fb-date {
  color: #888;
  font-size: 0.9em;
}

.fb-badges {
  display: flex;
  gap: 10px;
}

.fb-cat {
  background: #4ecdc4;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8em;
}

.fb-status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8em;
  font-weight: bold;
}

.fb-status.open {
  background: #ff6b6b;
  color: white;
}

.fb-status.in-progress {
  background: #ffa500;
  color: white;
}

.fb-status.resolved {
  background: #00ff00;
  color: black;
}

.fb-status.closed {
  background: #888;
  color: white;
}

.fb-content {
  margin-bottom: 15px;
}

.fb-location {
  margin-bottom: 8px;
  color: #666;
}

.fb-desc {
  margin-bottom: 10px;
  line-height: 1.5;
  color: #666;
}

.fb-contact {
  display: flex;
  gap: 20px;
  font-size: 0.9em;
  color: #666;
}

.admin-resp {
  background: #f0f8ff;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 10px;
}

.resp-date {
  font-size: 0.8em;
  color: #666;
  margin-top: 5px;
}

.fb-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.status-sel {
  padding: 5px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.fb-summary {
  background: #f9f9f9;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 15px;
  color:black;
}

</style>