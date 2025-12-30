<template>
  <div class="maincont">
    <header class="allhead">
      <h1>🎭 Mystical Feedback Portal 🎭</h1>
      <p>Share your cosmic experiences and suggestions...</p>
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

    <main class="dashboard-main">
      <section class="widget">
        <h2 class="widget-title">📊 Your Feedback Statistics</h2>
        <div class="widget-content">
          <div class="stats-grid">
            <div class="stat-card">
              <div class="stat-value">{{ fbhist.length }}</div>
              <div class="stat-label">Total Feedback</div>
            </div>
            <div class="stat-card">
              <div class="stat-value">{{ getstatus('Open') }}</div>
              <div class="stat-label">Open Issues</div>
            </div>
            <div class="stat-card">
              <div class="stat-value">{{ getstatus('In Progress') }}</div>
              <div class="stat-label">In Progress</div>
            </div>
            <div class="stat-card">
              <div class="stat-value">{{ getstatus('Resolved') }}</div>
              <div class="stat-label">Resolved</div>
            </div>
          </div>
        </div>
      </section>

      <section class="widget">
        <h2 class="widget-title">📝 Submit Cosmic Feedback</h2>
        <div class="widget-content">
          <form @submit.prevent="submitfb" class="fb-form">
            <div class="form-group">
              <label for="parking-lot">Sacred Ground:</label>
              <select v-model="feedbackForm.parking_lot_id" id="parking-lot"  >
                <option value="">Select a parking lot</option>
                <option v-for="lot in parkinglots" :key="lot.id" :value="lot.id">
                  {{ lot.name }}
                </option>
              </select>
            </div>

            <div class="form-group" v-if="feedbackForm.parking_lot_id">
              <label for="spot-number">Spot Number (Optional):</label>
              <select v-model="feedbackForm.spot_number" id="spot-number">
                <option value="">Select a spot (optional)</option>
                <option v-if="loadspots" disabled>Loading spots...</option>
                <option v-for="spot in avspots" :key="spot.id" :value="spot.spot_number">
                  Spot {{ spot.spot_number }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label for="issue_cat">Issue Category:</label>
              <select v-model="feedbackForm.issue_category" id="issue_cat"  >
                <option value="">Select category</option>
                <option value="Maintenance Issue">Facility Maintenance</option>
                <option value="Billing Problem">Payment Issues</option>
                <option value="Suggestion">General Suggestion</option>
                <option value="Other">Other</option>
                <option value="Spot Availability">Spot Availability</option>
                <option value="App/Website Issues">App/Website Issues</option>
                <option value="Customer Service">Customer Service</option>
                <option value="Pricing Concerns">Pricing Concerns</option>
                <option value="Safety/Security">Safety/Security</option>
                <option value="Accessibility">Accessibility</option>
              </select>
            </div>

            <div class="form-group">
              <label for="desc">Describe Your Experience:</label>
              <textarea v-model="feedbackForm.description" id="desc" rows="5" placeholder="Share your thoughts, suggestions, or issues..." >       
              </textarea>
            </div>

            <div v-if="feedbackErrors.length > 0" class="error-msgs">
              <ul>
                <li v-for="error in feedbackErrors" :key="error">{{ error }}</li>
              </ul>
            </div>

            <button type="submit" :disabled="subfb" class="btn-submit" >
              {{ subfb ? '⏳ Sending...' : '🚀 Send Feedback' }}
            </button>
          </form>
        </div>
      </section>

      <section class="widget">
        <h2 class="widget-title">📋 Your Feedback History</h2>
        <div class="widget-content">
          <div v-if="fbhist.length === 0" class="no-data">
            <p>No feedback submitted yet. Share your first experience above!</p>
          </div>
          
          <div v-else class="fb-list">
            <div v-for="feedback in fbhist" :key="feedback.id" class="fb-item" >
              <div class="fb-header">
                <div class="fb-meta">
                  <span class="fb-id">#{{ feedback.id }}</span>
                  <span class="fb-date">{{ formatdt(feedback.submitted_at) }}</span>
                </div>
                <div class="fb-badges">
                  <span class="fb-cat">{{ feedback.issue_category }}</span>
                  <span :class="statuscls(feedback.status)">{{ feedback.status }}</span>
                </div>
              </div>
              
              <div class="fb-content">
                <div v-if="feedback.parking_lot_name" class="fb-location">
                  <strong>Location:</strong> {{ feedback.parking_lot_name }}
                  <span v-if="feedback.spot_number"> - Spot {{ feedback.spot_number }}</span>
                </div>
                <div class="fb-desc">{{ feedback.description }}</div>
              </div>
              
              <div v-if="feedback.admin_response" class="admin-resp">
                <h5>Admin Response:</h5>
                <p>{{ feedback.admin_response }}</p>
                <div class="resp-date">{{ formatdt(feedback.updated_at) }}</div>
              </div>
            </div>
          </div>
        </div>
      </section>

    </main>
  </div>
</template>

<script>
export default {
  name: 'userfb',
  data() {
    return {
      userprofile: {},
      parkinglots: [],
      avspots: [],
      loadspots: false,
      fbhist: [],
      feedbackForm: {
        parking_lot_id: '',
        spot_number: '',
        issue_category: '',
        description: ''
      },
      feedbackErrors: [],
      subfb: false,
      showlogout: false
    };
  },
  watch: {
    'feedbackForm.parking_lot_id'(newLotId) {
      if (newLotId) {
        this.fetchspots(newLotId);
      }
      else{
        this.avspots = [];
      }
      this.feedbackForm.spot_number = '';
    }
  },
  async mounted() {
    await this.checkauth();
    await this.fetchuprof();
    await this.fetchuplots();
    await this.fetchfbhist();
  },
  methods: {
    async checkauth() {
      const token = localStorage.getItem('access_token');
      if (!token) {
        this.$router.push('/');
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

    async fetchuprof() {
      try {
        const resp = await this.makeauthreq('/api/profile');
        if (resp && resp.ok) {
          this.userprofile = await resp.json();
        }
      } catch (error) {
        console.error('Error fetching user profile:', error);
      }
    },

    async fetchuplots() {
      try {
        const resp = await this.makeauthreq('/api/user/parking-lots');
        if (resp && resp.ok) {
          const data = await resp.json();
          this.parkinglots = data.parking_lots || [];
        }
      } catch (error) {
        console.error('Error fetching parking lots:', error);
      }
    },

    async fetchspots(lotid) {
      this.loadspots = true;
      try {
        const resp = await this.makeauthreq(`/api/user/parking-lots/${lotid}/spots`);
        if (resp && resp.ok) {
          const data = await resp.json();
          this.avspots = data.spots || [];
        }
      } catch (error) {
        console.error('Error fetching spots:', error);
        this.avspots = [];
      } finally {
        this.loadspots = false;
      }
    },

    async fetchfbhist() {
      try {
        const resp = await this.makeauthreq('/api/user/feedback');
        if (resp && resp.ok) {
          const data = await resp.json();
          this.fbhist = data.feedback || [];
          this.fbhist.sort((a, b) => new Date(b.submitted_at) - new Date(a.submitted_at));
        }
      } catch (error) {
        console.error('Error fetching feedback history:', error);
      }
    },

    async submitfb() {
      this.feedbackErrors = [];
      this.subfb = true;

      if (!this.feedbackForm.parking_lot_id) {
        this.feedbackErrors.push('Please select a parking lot');
      }
      if (!this.feedbackForm.issue_category) {
        this.feedbackErrors.push('Please select an issue category');
      }
      if (!this.feedbackForm.description.trim()) {
        this.feedbackErrors.push('Please provide a description');
      }

      if (this.feedbackErrors.length > 0) {
        this.subfb = false;
        return;
      }

      try {
        const selectedLot = this.parkinglots.find(lot => lot.id == this.feedbackForm.parking_lot_id);
        const feedbackData = {
          ...this.feedbackForm,
          parking_lot_name: selectedLot ? selectedLot.name : ''
        };

        console.log('Submitting feedback:', feedbackData);
        const resp = await this.makeauthreq('/api/user/feedback', {
          method: 'POST',
          body: JSON.stringify(feedbackData)
        });

        console.log('Response status:', resp?.status);

        if (resp && resp.ok) {
          alert('✅ Feedback submitted successfully! We will review it and get back to you.');

          this.feedbackForm = {
            parking_lot_id: '',
            spot_number: '',
            issue_category: '',
            description: ''
          };
          this.avspots = [];
          await this.fetchfbhist();
        } 
        else if (resp) {
          const data = await resp.json();
          console.error('Feedback submission error:', data);
          if (data.errors && Array.isArray(data.errors)) {
            alert(`❌ Error: ${data.errors.join(', ')}`);
          } 
          else {
            alert(`❌ Error: ${data.message || 'Failed to submit feedback'}`);
          }
        }
      } catch (error) {
        console.error('Error submitting feedback:', error);
        alert('❌ Error submitting feedback. Please try again.');
      } finally {
        this.subfb = false;
      }
    },

    statuscls(st) {
      return {
        'fb-status': true,
        'open': st === 'Open',
        'in-progress': st === 'In Progress',
        'resolved': st === 'Resolved',
        'closed': st === 'Closed'
      };
    },

    getstatus(st) {
      return this.fbhist.filter(feedback => feedback.status === st).length;
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
      const role = localStorage.getItem('user_role');
      if (role === 'admin') {
        this.$router.push('/admin');
      } 
      else {
        this.$router.push('/dashboard');
      }
    }
  }
}
</script>