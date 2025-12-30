<template>
  <div class="maincont">
    <header class="allhead">
      <h1>👤 Your Profile</h1>
      <p>Manage your account information</p>
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
      <h2 class="widget-title">📋 Profile Information</h2>
      <div class="widget-content">
        <div v-if="loading" class="loading">
          <p>Loading profile...</p>
        </div>
        <div v-else-if="error" class="error">
          <p>{{ error }}</p>
          <button @click="loadprof" class="btn-primary">Retry</button>
        </div>
        <div v-else class="user-profile">
          <div class="prof-sec">
            <h3>Personal Information</h3>
            <div v-if="!editmode">
              <div class="profile-field">
                <label>Username:</label>
                <span>{{ user.username }}</span>
              </div>
              <div class="profile-field">
                <label>Email:</label>
                <span>{{ user.email}}</span>
              </div>
              <div class="profile-field">
                <label>Phone Number:</label>
                <span>{{ user.phone_number }}</span>
              </div>
              <div class="profile-field">
                <label>Member Since:</label>
                <span>{{ formatdt(user.created_at) }}</span>
              </div>
              <button @click="entereditmode" class="btn-primary">✏️ Edit Profile</button>
            </div>
            
            <div v-else>
              <form @submit.prevent="updprof">
                <div class="form-group">
                  <label for="edit-email">Email:</label>
                  <input type="email" id="edit-email" v-model="editdata.email" :class="{ 'input-error': upderror && upderror.includes('email') }">
                </div>
                <div class="form-group">
                  <label for="edit-phone">Phone Number:</label>
                  <input type="text" id="edit-phone" v-model="editdata.phone_number" 
                  :class="{ 'input-error': upderror && upderror.includes('phone') }">
                </div>
                <div v-if="upderror" class="error-msg">
                  {{ upderror }}
                </div>
                <div class="form-actions">
                  <button type="submit" :disabled="updating" class="btn-primary">
                    {{ updating ? '⏳ Updating...' : '💾 Save Changes' }}
                  </button>
                  <button type="button" @click="closeedit" class="btn-secondary">❌ Cancel</button>
                </div>
              </form>
            </div>
          </div>

          <div class="prof-sec">
            <h3>Loyalty Points</h3>
            <div>
              <div>
                <span>Points Available: </span>
                <span>{{ user.loyalty_points }}</span>
              </div>
              <div>
                <span>Discount Value: </span>
                <span>${{ ((user.loyalty_points) / 10).toFixed(2) }}</span>
              </div>
              <p class="points-info">Earn 1 point for every 30 minutes of parking. 10 points = $1 discount.</p>
            </div>
          </div>

          <div class="prof-sec">
            <h3>📊 Export My Data</h3>
            <div class="export-info">
              <p>Download your complete parking history as a CSV file.</p>
              <button @click="expmyhist" :disabled="exportload" class="btn-primary export-btn">
                {{ exportload ? '⏳ Preparing Export...' : '📥 Export My History' }}
              </button>
              <div v-if="expmsg" class="exp-msg" :class="{ 'success': expsucc, 'error': !expsucc }">
                {{ expmsg }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="widget">
      <h2 class="widget-title">🔐 Change Password</h2>
      <div class="widget-content">
        <div v-if="!pwdchangemode">
          <p>Update your account password for better security.</p>
          <button @click="enterpwdchangemode" class="btn-primary">🔑 Change Password</button>
        </div>
        
        <div v-else>
          <form @submit.prevent="changepwd">
            <div class="form-group">
              <label for="currpwd">Current Password:</label>
              <input type="password" id="currpwd" v-model="pwddata.current_password"
                :class="{ 'input-error': pwderror && pwderror.includes('current') }">
            </div>
            <div class="form-group">
              <label for="newpwd">New Password:</label>
              <input type="password" id="newpwd" v-model="pwddata.new_password"
                @input="checkknewpwdreq" :class="{ 'input-error': pwderror && pwderror.includes('new') }">
              
              <div v-if="!Object.values(newpwdcheck).every(check => check)">
                <div class="req" :class="{ 'met': newpwdcheck.length }">
                  <i class="fas fa-check" v-if="newpwdcheck.length"></i>
                  <i class="fas fa-times" v-else></i>
                  Minimum 6 characters
                </div>
                <div class="req" :class="{ 'met': newpwdcheck.uppercase }">
                  <i class="fas fa-check" v-if="newpwdcheck.uppercase"></i>
                  <i class="fas fa-times" v-else></i>
                  At least 1 uppercase letter
                </div>
                <div class="req" :class="{ 'met': newpwdcheck.lowercase }">
                  <i class="fas fa-check" v-if="newpwdcheck.lowercase"></i>
                  <i class="fas fa-times" v-else></i>
                  At least 1 lowercase letter
                </div>
                <div class="req" :class="{ 'met': newpwdcheck.number }">
                  <i class="fas fa-check" v-if="newpwdcheck.number"></i>
                  <i class="fas fa-times" v-else></i>
                  At least 1 number
                </div>
                <div class="req" :class="{ 'met': newpwdcheck.symbol }">
                  <i class="fas fa-check" v-if="newpwdcheck.symbol"></i>
                  <i class="fas fa-times" v-else></i>
                  At least 1 symbol
                </div>
              </div>
            </div>
            <div class="form-group">
              <label for="conf-pwd">Confirm New Password:</label>
              <input type="password" id="conf-pwd" v-model="pwddata.confirm_password" :class="{ 'input-error': pwderror && pwderror.includes('confirm') }">
            </div>
            <div v-if="pwderror" class="error-msg">
              {{ pwderror }}
            </div>
            <div class="form-actions">
              <button type="submit" :disabled="changingpwd" class="btn-primary">
                {{ changingpwd ? '⏳ Changing...' : '🔐 Change Password' }}
              </button>
              <button type="button" @click="clpwdchange" class="btn-secondary">❌ Cancel</button>
            </div>
          </form>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import { showToast } from '../utils/toast.js'

export default {
  name: 'userProfile',
  data() {
    return {
      user: {},
      totres: 0,
      loading: true,
      error: null,
      accessToken: localStorage.getItem('access_token'),
      editmode: false,
      editdata: {},
      updating: false,
      upderror: null,
      pwdchangemode: false,
      pwddata: {
        current_password: '',
        new_password: '',
        confirm_password: ''
      },
      showlogout: false,
      logouttimer: null,
      changingpwd: false,
      pwderror: null,
      newpwdcheck: {
        length: false,
        uppercase: false,
        lowercase: false,
        number: false,
        symbol: false
      },
      exportload: false,
      expmsg: '',
      expsucc: false
    };
  },
  async mounted() {
    if (!this.accessToken) {
      this.$router.push('/');
      return;
    }
    await this.loadprof();
    await this.loadrescount();
  },
  methods: {
    async makeauthreq(url, options = {}) {
      const headers = {
        'Authorization': `Bearer ${this.accessToken}`,
        'Content-Type': 'application/json',
        ...options.headers
      };
      
      const resp = await fetch(url, {
        ...options,headers 
      });
      
      if (resp.status === 401) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        this.$router.push('/');
        return null;
      }
      
      return resp;
    },

    async loadprof() {
      try {
        this.loading = true;
        this.error = null;
        const resp = await this.makeauthreq('/api/profile');
        
        if (resp && resp.ok) {
          const data = await resp.json();
          this.user = data.user || {};
        } 
        else {
          this.error = 'Failed to load profile';
        }
      } 
      catch (error) {
        console.error('Error loading profile:', error);
        this.error = 'Error loading profile';
      } 
      finally {
        this.loading = false;
      }
    },

    async loadrescount() {
      try {
        const resp = await this.makeauthreq('/api/user/reservations');
        if (resp && resp.ok) {
          const data = await resp.json();
          this.totres = data.reservations ? data.reservations.length : 0;
        }
      } 
      catch (error) {
        console.error('Error loading reservation count:', error);
      }
    },

    entereditmode() {
      this.editmode = true;
      this.editdata = {
        email: this.user.email || '',
        phone_number: this.user.phone_number || ''
      };
      this.upderror = null;
    },
    

    closeedit() {
      this.editmode = false;
      this.editdata = {};
      this.upderror = null;
    },

    async updprof() {
      try {
        this.updating = true;
        this.upderror = null;
        
        const resp = await this.makeauthreq('/api/user/update-profile', {
          method: 'PUT',
          body: JSON.stringify(this.editdata)
        });
        
        if (resp && resp.ok) {
          const data = await resp.json();
          if (data.success && data.user) {
            this.user = { ...this.user, ...data.user };
            this.editmode = false;
            showToast.profileUpdated();
          } 
          else {
            this.upderror = data.message || 'Failed to update profile';
          }
        } 
        else if (resp) {
          const data = await resp.json();
          this.upderror = data.message || 'Failed to update profile';
        }
      } 
      catch (error) {
        console.error('Error updating profile:', error);
        this.upderror = 'Error updating profile';
      } 
      finally {
        this.updating = false;
      }
    },

    enterpwdchangemode() {
      this.pwdchangemode = true;
      this.pwddata = {
        current_password: '',
        new_password: '',
        confirm_password: ''
      };
      this.pwderror = null;
      this.newpwdcheck = {
        length: false,
        uppercase: false,
        lowercase: false,
        number: false,
        symbol: false
      };
    },

    clpwdchange() {
      this.pwdchangemode = false;
      this.pwddata = {
        current_password: '',
        new_password: '',
        confirm_password: ''
      };
      this.pwderror = null;
    },

    checkknewpwdreq() {
      const password = this.pwddata.new_password;
      this.newpwdcheck.length = password.length >= 6;
      this.newpwdcheck.uppercase = /[A-Z]/.test(password);
      this.newpwdcheck.lowercase = /[a-z]/.test(password);
      this.newpwdcheck.number = /\d/.test(password);
      this.newpwdcheck.symbol = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password);
    },

    async changepwd() {
      try {
        this.changingpwd = true;
        this.pwderror = null;

        if (!this.pwddata.current_password) {
          this.pwderror = 'Current password is required';
          return;
        }

        if (!this.pwddata.new_password) {
          this.pwderror = 'New password is required';
          return;
        }

        if (!Object.values(this.newpwdcheck).every(check => check)) {
          this.pwderror = 'New password does not meet all requirements';
          return;
        }

        if (this.pwddata.new_password !== this.pwddata.confirm_password) {
          this.pwderror = 'Password confirmation does not match';
          return;
        }

        const resp = await this.makeauthreq('/api/user/change-password', {
          method: 'POST',
          body: JSON.stringify({
            current_password: this.pwddata.current_password,
            new_password: this.pwddata.new_password,
            confirm_password: this.pwddata.confirm_password
          })
        });

        if (resp && resp.ok) {
          showToast.success('Password changed successfully! 🔒');
          this.clpwdchange();
        } 
        else if (resp) {
          const data = await resp.json();
          this.pwderror = data.message || 'Failed to change password';
        }
      } 
      catch (error) {
        console.error('Error changing password:', error);
        this.pwderror = 'Error changing password';
      } 
      finally {
        this.changingpwd = false;
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

    logout(){
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_role');
      this.$router.push('/');
    },

    async expmyhist() {
      this.exportload = true;
      this.expmsg = '';
      this.expsucc = false;

      try {
        const resp = await this.makeauthreq('/api/user/export-my-history', {
          method: 'POST'
        });

        if (resp && resp.ok) {
          const data = await resp.json();
          this.expmsg = data.message;
          this.expsucc = data.success;
        } 
        else {
          const errorData = await resp.json();
          this.expmsg = errorData.message || 'Export failed. Please try again.';
          this.expsucc = false;
        }
      } 
      catch (error) {
        console.error('Export error:', error);
        this.expmsg = 'An error occurred while exporting your history.';
        this.expsucc = false;
      } 
      finally {
        this.exportload = false;
        setTimeout(() => {
          this.expmsg = '';
        }, 5000);
      }
    },

    goback() {
      const urole = localStorage.getItem('user_role');
      if (urole === 'admin') {
        this.$router.push('/admin');
      } else {
        this.$router.push('/dashboard');
      }
    }
  }
}
</script>

<style scoped>
.export-info {
  text-align: center;
  padding: 20px;
}

.export-btn {
  margin-top: 15px;
  padding: 12px 24px;
  font-size: 16px;
  min-width: 200px;
}

.export-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.exp-msg {
  margin-top: 15px;
  padding: 10px;
  border-radius: 5px;
  font-weight: bold;
}

.exp-msg.success {
  background-color: rgba(0, 255, 0, 0.1);
  color: #00ff00;
  border: 1px solid rgba(0, 255, 0, 0.3);
}

.exp-msg.error {
  background-color: rgba(255, 0, 0, 0.1);
  color: #ff4444;
  border: 1px solid rgba(255, 0, 0, 0.3);
}
</style>