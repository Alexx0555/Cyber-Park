<template>
  <div class="maincont">
    <div class="booth">
      <div class="curt curt-l"></div>
      <div class="curt curt-r"></div>
      <div class="board">
        <h1>{{ islogin ? '🤫 Confess Your Credentials 🤫' : '✨ Join the Congregation ✨' }}</h1>
      </div>
        <div v-if="islogin" class="cont">
          <h2>Login</h2>
          <form @submit.prevent="login">
            <div class="form-group">
              <label>Username:</label>
              <input type="text" v-model="loginForm.uname" :class="{ 'input-error': loginErrors.uname }">
              <p v-if="loginErrors.uname" class="error-msg">{{ loginErrors.uname }}</p>
            </div>
            <div class="form-group">
              <label>Password:</label>
              <div class="pwd-inp">
                <input :type="showlogpwd ? 'text' : 'password'"  v-model="loginForm.pwd" :class="{ 'input-error': loginErrors.pwd }" >
                <button type="button" class="pwd-toggle" @click="toglogpwd" :title="showlogpwd ? 'Hide password' : 'Show password'">
                  {{ showlogpwd ? '🙈' : '👁️' }}
                </button>
              </div>
              <p v-if="loginErrors.pwd" class="error-msg">{{ loginErrors.pwd }}</p>
            </div>
            <button type="submit" class="btn-submit">Enter the Chamber 🚪</button>
            <p class="toggle-form">
              Need to confess something new? 
              <a href="#" @click.prevent="toggleForm">Register Here</a>
            </p>
          </form>
        </div>

        <div v-else class="cont">
          <h2>Register</h2>
          <form @submit.prevent="reg">
            <div class="form-group">
              <label for="reg-uname">Provide your Username:</label>
              <input type="text" id="reg-uname" v-model="registerForm.uname" :class="{ 'input-error': registerErrors.uname }" >
              <p v-if="registerErrors.uname" class="error-msg">{{ registerErrors.uname }}</p>
            </div>
            <div class="form-group">
              <label for="reg-email">Secret Email <i class="fas fa-envelope"></i></label>
              <input 
                type="email" id="reg-email" v-model="registerForm.email" :class="{ 'input-error': registerErrors.email }" >
              <p v-if="registerErrors.email" class="error-msg">{{ registerErrors.email }}</p>
            </div>
            <div class="form-group">
              <label for="reg-phone">Phone Number <i class="fas fa-phone"></i></label>
              <input type="text" inputmode="numeric" id="reg-phone" v-model="registerForm.phone" pattern="\d{10}" title="Phone number must be exactly 10 digits":class="{ 'input-error': registerErrors.phone }">
              <p v-if="registerErrors.phone" class="error-msg">{{ registerErrors.phone }}</p>
            </div>
            <div class="form-group">
              <label for="reg-pwd">Create Your Secret Code:</label>
              <div class="pwd-inp">
                <input :type="showregpwd ? 'text' : 'password'" id="reg-pwd" v-model="registerForm.pwd" :class="{ 'input-error': registerErrors.pwd }" @input="checkpwd">
                <button type="button" class="pwd-toggle" @click="togregpwd" :title="showregpwd ? 'Hide password' : 'Show password'">
                  {{ showregpwd ? '🙈' : '👁️' }}
                </button>
              </div>
              <p v-if="registerErrors.pwd" class="error-msg">{{ registerErrors.pwd }}</p>
              
              <div class="pwd-req">
                <div class="req" :class="{ 'met': pwdChecks.hasup }">
                  <i class="fas fa-check" v-if="pwdChecks.hasup"></i>
                  <i class="fas fa-times" v-else></i>
                  At least 1 uppercase letter
                </div>
                <div class="req" :class="{ 'met': pwdChecks.haslow }">
                  <i class="fas fa-check" v-if="pwdChecks.haslow"></i>
                  <i class="fas fa-times" v-else></i>
                  At least 1 lowercase letter
                </div>
                <div class="req" :class="{ 'met': pwdChecks.hassym }">
                  <i class="fas fa-check" v-if="pwdChecks.hassym"></i>
                  <i class="fas fa-times" v-else></i>
                  At least 1 symbol
                </div>
                <div class="req" :class="{ 'met': pwdChecks.hasnum }">
                  <i class="fas fa-check" v-if="pwdChecks.hasnum"></i>
                  <i class="fas fa-times" v-else></i>
                  At least 1 number
                </div>
                <div class="req" :class="{ 'met': pwdChecks.hasmlen }">
                  <i class="fas fa-check" v-if="pwdChecks.hasmlen"></i>
                  <i class="fas fa-times" v-else></i>
                  Minimum 6 characters
                </div>
              </div>
            </div>
            <button type="submit" class="btn-submit">Join the Congregation 🎭</button>
            <p class="toggle-form">
              Already a member? 
              <a href="#" @click.prevent="toggleForm">Login Here</a>
            </p>
          </form>
        </div>
    </div>
  </div>
</template>

<script>
import { showToast } from '../utils/toast.js'

export default {
  name: 'logreg',
  data() {
    return {
      islogin: true,
      loginForm: {
        uname: '',
        pwd: ''
      },
      registerForm: {
        uname: '',
        email: '',
        phone: '',
        pwd: ''
      },
      loginErrors: {
        uname: '',
        pwd: ''
      },
      registerErrors: {
        uname: '',
        email: '',
        phone: '',
        pwd: ''
      },
      pwdChecks: {
        hasup: false,
        haslow: false,
        hassym: false,
        hasnum: false,
        hasmlen: false
      },
      showlogpwd: false,
      showregpwd: false
    };
  },
  methods: {
    toggleForm() {
      this.islogin = !this.islogin;
      this.resetErrors();
      this.resetForms();
    },

    valmail(email) {
      const re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
      return re.test(String(email).toLowerCase());
    },

    resetErrors() {
      this.loginErrors = { uname: '', pwd: '' };
      this.registerErrors = { uname: '', email: '', pwd: '', phone: '' };
    },

    resetForms() {
      this.loginForm = { uname: '', pwd: '' };
      this.registerForm = { uname: '', email: '', pwd: '', phone: '' };
    },

    checkpwd() {
      const pwd = this.registerForm.pwd;
      this.pwdChecks.hasup = /[A-Z]/.test(pwd);
      this.pwdChecks.haslow = /[a-z]/.test(pwd);
      this.pwdChecks.hassym = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(pwd);
      this.pwdChecks.hasnum = /\d/.test(pwd);
      this.pwdChecks.hasmlen = pwd.length >= 6;
    },

    toglogpwd() {
      this.showlogpwd = !this.showlogpwd;
    },

    togregpwd() {
      this.showregpwd = !this.showregpwd;
    },

    async login() {
      this.resetErrors();
      
      if (!this.loginForm.uname.trim()) {
        this.loginErrors.uname = 'Username is required';
        return;
      }
      if (!this.loginForm.pwd) {
        this.loginErrors.pwd = 'Password is required';
        return;
      }

      try {
        const resp = await fetch('/api/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(this.loginForm)
        });

        const data = await resp.json();

        if (resp.ok) {
          localStorage.setItem('access_token', data.access_token);
          localStorage.setItem('refresh_token', data.refresh_token);
          localStorage.setItem('user_role', data.user_role);

          showToast.loginSuccess(data.username || this.loginForm.uname);

          if (data.user_role === 'admin') {
            this.$router.push('/admin');
          } else {
            this.$router.push('/dashboard');
          }
        } else {
          if (data.field_errors) {
            this.loginErrors = { ...this.loginErrors, ...data.field_errors };
          } else {
            showToast.loginError(data.message || 'Login failed');
          }
        }
      } catch (error) {
        console.error('Login error:', error);
        showToast.networkError();
      }
    },

    async reg() {
      this.resetErrors();
      
      if (!this.registerForm.uname.trim()) {
        this.registerErrors.uname = 'Username is required';
        return;
      }
      if (!this.registerForm.email.trim()) {
        this.registerErrors.email = 'Email is required';
        return;
      }
      if (!this.valmail(this.registerForm.email)) {
        this.registerErrors.email = 'Please enter a valid email address';
        return;
      }
      if (!this.registerForm.phone.trim()) {
        this.registerErrors.phone = 'Phone number is required';
        return;
      }
      if (!this.registerForm.pwd) {
        this.registerErrors.pwd = 'Password is required';
        return;
      }

      if (!Object.values(this.pwdChecks).every(check => check)) {
        this.registerErrors.pwd = 'Password does not meet all requirements';
        return;
      }

      try {
        const resp = await fetch('/api/register', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(this.registerForm)
        });

        const data = await resp.json();

        if (resp.ok) {
          showToast.success('Registration successful! Please login with your credentials. 🎉');
          this.islogin = true;
          this.resetForms();
        } else {
          if (data.field_errors) {
            this.registerErrors = { ...this.registerErrors, ...data.field_errors };
          } else {
            showToast.error(data.message || 'Registration failed');
          }
        }
      } catch (error) {
        console.error('Registration error:', error);
        showToast.networkError();
      }
    }
  }
}
</script>
