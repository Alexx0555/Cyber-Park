<template>
  <div class="maincont">
    <header class="allhead">
      <h1>🚗 Welcome to CyberPark Dashboard 🚗</h1>
      <p>Your parking management portal</p>
      <div class="user-info" style="display: flex; justify-content: space-between; align-items: center;">
        <span>Welcome, <strong>{{ user.username }}</strong>!</span>
        <div class="nav-buttons">
          <button @click="gotoprof" class="btn-secondary">👤 Profile</button>
          <button @click="gotohist" class="btn-secondary">📜 History</button>
          <button @click="gotofb" class="btn-secondary">🎭 Feedback</button>
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
      <h2 class="widget-title">📍 Available Parking Lots</h2>
      <div class="widget-content">
        <div v-if="parkinglots.length === 0" class="no-data">
          <p>No parking lots available at the moment.</p>
        </div>
        <ul class="item-list" v-else>
          <li v-for="lot in parkinglots" :key="lot.id">
            <div class="item-info">
              <span><strong>{{ lot.name }}</strong></span>
              <p class="item-subtext">{{ lot.location }}</p>
              <p class="item-subtext">Price: ${{ lot.price_per_hour }}/hour</p>
              <p class="item-subtext" :class="{'status-ok': lot.available > 0, 'status-full': lot.available === 0}">
                Available: {{ lot.available }} / {{ lot.capacity }}
              </p>
            </div>
            <div class="item-actions">
              <button @click="viewlotspots(lot)" class="btn-secondary" :disabled="lot.available === 0">
                {{ lot.available === 0 ? 'Full' : 'View Spots' }}
              </button>
            </div>
          </li>
        </ul>
      </div>
    </section>

    <section class="widget" v-if="selectedlot">
      <h2 class="widget-title">🅿️ {{ selectedlot.name }} Parking Layout</h2>
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
                </div>
              </div>
            </div>
          </div>
          <div class="parking-exit">🚪 EXIT 🚪 </div>
        </div>
      </div>
    </section>

    <section class="widget" v-if="actres.length > 0">
      <h2 class="widget-title">🚗 Your Active Reservations</h2>
      <div class="widget-content">
        <ul class="item-list">
          <li v-for="res in actres" :key="res.id">
            <div class="item-info">
              <span><strong>{{ res.prime_location_name }}</strong></span>
              <p class="item-subtext">Spot: {{ res.spot_number }}</p>
              <p class="item-subtext">Vehicle: {{ res.vehicle_number }}</p>
              <p class="item-subtext">Started: {{ formatdt(res.parking_timestamp) }}</p>
              <p class="item-subtext">Duration: {{ calcdur(res.parking_timestamp) }}</p>
              <p class="item-subtext">Current Cost: ${{ calcurrcost(res).toFixed(2) }}</p>
            </div>
            <div class="item-actions">
              <button @click="openrelmodal(res)" class="btn-danger">🚪 Release Spot</button>
            </div>
          </li>
        </ul>
      </div>
    </section>

    <section class="widget">
      <h2 class="widget-title">📊 Your Parking Statistics</h2>
      <div class="widget-content">
        <div v-if="reservations.length === 0">
          <p>No bookings found.</p>
        </div>
        <div v-else class="charts-container">
          <div class="chart-item">
            <h3>Monthly Sessions</h3>
            <canvas id="sessionchart"></canvas>
          </div>
          <div class="chart-item">
            <h3>Monthly Spending</h3>
            <canvas id="spendingchart"></canvas>
          </div>
        </div>
      </div>
    </section>

    <div v-if="showbookingmodal" class="modal-overlay" @click="clbookingmodal">
      <div class="modal-content" @click.stop>
        <h3>🎫 Choose Your Action</h3>
        <div v-if="selectedspot">
          <p><strong>Location:</strong> {{ selectedlot.name }}</p>
          <p><strong>Spot:</strong> {{ selectedspot.spot_number }}</p>
          <p><strong>Price:</strong> ${{ selectedlot.price_per_hour }}/hour</p>
          <p v-if="selectedspot.vehicle_type"><strong>Vehicle Type:</strong> {{ selectedspot.vehicle_type }}</p>
        </div>

        <div class="form-group">
          <label for="veh_num">Vehicle Number:</label>
          <input type="text" id="veh_num" v-model="bookingdata.vehicle_number" 
          :class="{ 'input-error': vehnumerror }" placeholder="e.g., AB12C1234">
          <p v-if="vehnumerror" class="error-msg">{{ vehnumerror }}</p>
        </div>

        <div class="form-group" v-if="user.loyalty_points > 0">
          <label for="redeem_pts">Redeem Loyalty Points ({{ user.loyalty_points }} available):</label>
          <input type="number" id="redeem_pts" v-model="bookingdata.points_to_redeem" :max="user.loyalty_points" min="0">
          <p class="info-text">10 points = $1 discount</p>
        </div>

        <div class="booking-options">
          <div class="option-card">
            <h4>📅 Book Only</h4>
            <p>Reserve the spot for 12 hours. No billing starts until you occupy it.</p>
            <button @click="confbooking" class="btn-book">Book Spot</button>
          </div>
          <div class="option-card">
            <h4>🚗 Occupy Now</h4>
            <p>Immediately start using the spot. Billing begins right away.</p>
            <button @click="confoccup" class="btn-occupy">Occupy Now</button>
          </div>
        </div>

        <div class="modal-actions">
          <button @click="clbookingmodal" class="btn-secondary">❌ Cancel</button>
        </div>
      </div>
    </div>

    <div v-if="showoccupmodal" class="modal-overlay" @click="cloccupmodal">
      <div class="modal-content" @click.stop>
        <h3>🚗 Occupy Your Booked Spot</h3>
        <div v-if="selectedspot">
          <p><strong>Location:</strong> {{ selectedlot.name }}</p>
          <p><strong>Spot:</strong> {{ selectedspot.spot_number }}</p>
          <p><strong>Vehicle:</strong> {{ selectedspot.vehicle_number }}</p>
          <p><strong>Booking Expires:</strong> {{ new Date(selectedspot.booking_expires_at).toLocaleString() }}</p>
          <p class="info-text">💡 Click "Occupy Now" to start billing for this spot.</p>
        </div>

        <div class="modal-actions">
          <button @click="confbkoccup" class="btn-primary">🚗 Occupy Now</button>
          <button @click="cancbooking" class="btn-danger">🗑️ Cancel Booking</button>
          <button @click="cloccupmodal" class="btn-secondary">❌ Close</button>
        </div>
      </div>
    </div>

    <div v-if="showrelmodal" class="modal-overlay" @click="closerelmodal">
      <div class="modal-content" @click.stop>
        <h3>🚪 Release Parking Spot</h3>
        <div v-if="selectedres">
          <p><strong>Location:</strong> {{ selectedres.prime_location_name }}</p>
          <p><strong>Spot:</strong> {{ selectedres.spot_number }}</p>
          <p><strong>Vehicle:</strong> {{ selectedres.vehicle_number }}</p>
          <p><strong>Duration:</strong> {{ calcdur(selectedres.parking_timestamp) }}</p>
          <p><strong>Total Cost:</strong> ${{ calcurrcost(selectedres).toFixed(2) }}</p>
        </div>
        
        <div class="modal-actions">
          <button @click="confrel" class="btn-danger">🚪 Confirm Release</button>
          <button @click="closerelmodal" class="btn-secondary">❌ Cancel</button>
        </div>
      </div>
    </div>

    <div v-if="showrelsucmodal" class="modal-overlay" @click="clrelsucmodal">
      <div class="modal-content" @click.stop>
        <h3>✅ Spot Released Successfully!</h3>
        <div v-if="reldetails">
          <p><strong>Location:</strong> {{ reldetails.prime_location_name }}</p>
          <p><strong>Spot:</strong> {{ reldetails.spot_number }}</p>
          <p><strong>Duration:</strong> {{ reldetails.duration }}</p>
          <p><strong>Total Cost:</strong> ${{ reldetails.total_cost }}</p>
          <p><strong>Points Earned:</strong> {{ reldetails.points_earned }}</p>
        </div>
        
        <div class="modal-actions">
          <button @click="clrelsucmodal" class="btn-primary">👍 Great!</button>
        </div>
      </div>
    </div>

    <div v-if="showvehconflictmodal" class="modal-overlay" @click="clvehconflictmodal">
      <div class="modal-content" @click.stop>
        <h3>⚠️ Vehicle Already Parked</h3>
        <div v-if="vehconflictdata">
          <p>Vehicle <strong>{{ vehconflictdata.vehicle_number }}</strong> is already parked at:</p>
          <p><strong>Location:</strong> {{ vehconflictdata.prime_location_name }}</p>
          <p><strong>Spot:</strong> {{ vehconflictdata.spot_number }}</p>
          <p><strong>Since:</strong> {{ formatdt(vehconflictdata.parking_timestamp) }}</p>
        </div>
        
        <div class="modal-actions">
          <button @click="clvehconflictmodal" class="btn-primary">👍 Got it</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { showToast } from '../utils/toast.js'

export default {
  name: 'userdash',
  data() {
    return {
      user: {},
      parkinglots: [],
      selectedlot: null,
      avspots: [],
      selectedspot: null,
      reservations: [],
      actres: [],
      showbookingmodal: false,
      showoccupmodal: false,
      showrelmodal: false,
      showrelsucmodal: false,
      selectedres: null,
      reldetails: null,
      bookingdata: {
        vehicle_number: '',
        points_to_redeem: 0
      },
      vehnumerror: null,
      showlogout: false,
      logouttimer: null,
      showvehconflictmodal: false,
      vehconflictdata: null,
      accessToken: localStorage.getItem('access_token'),
      sessionchart: null,
      spendingchart: null
    }
  },
  async mounted() {
    if (!this.accessToken) {
      this.$router.push('/');
      return;
    }

    await this.loaduserprof();
    await this.loadparkinglots();
    await this.loadres();
    await this.loadactres();

    setTimeout(() => {
      this.createucharts();
    }, 1000);
  },
  computed: {
    parkingrows() {
      if (!this.avspots.length) return [];

      const spotsperrow = 5;
      const rows = [];

      const sortspots = [...this.avspots].sort((a, b) => {
        const n1 = parseInt(a.spot_number) || 0;
        const n2 = parseInt(b.spot_number) || 0;
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

    async loaduserprof() {
      try {
        const resp = await this.makeauthreq('/api/profile');
        if (resp && resp.ok) {
          const data = await resp.json();
          this.user = data.user || {};
        }
      } 
      catch (error) {
        console.error('Error loading user profile:', error);
      }
    },

    async loadparkinglots() {
      try {
        const resp = await this.makeauthreq('/api/user/parking-lots');
        if (resp && resp.ok) {
          const data = await resp.json();
          this.parkinglots = data.parking_lots || [];
        }
      } 
      catch (error) {
        console.error('Error loading parking lots:', error);
      }
    },

    async loadres() {
      try {
        const resp = await this.makeauthreq('/api/user/reservations');
        if (resp && resp.ok) {
          const data = await resp.json();
          this.reservations = data.reservations || [];
        }
      } 
      catch (error) {
        console.error('Error loading reservations:', error);
      }
    },

    async loadactres() {
      try {
        const resp = await this.makeauthreq('/api/user/active-reservations');
        if (resp && resp.ok) {
          const data = await resp.json();
          this.actres = data.active_reservations || [];
        }
      } 
      catch (error) {
        console.error('Error loading active reservations:', error);
      }
    },

    async viewlotspots(lot) {
      this.selectedlot = lot;
      try {
        const resp = await this.makeauthreq(`/api/user/parking-lots/${lot.id}/spots`);
        if (resp && resp.ok) {
          const data = await resp.json();
          this.avspots = data.spots || [];
        }
      } 
      catch (error) {
        console.error('Error loading spots:', error);
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
      else if (spot.is_booked) {
        classes.push('booked');
        if (spot.booked_by_current_user) {
          classes.push('booked-by-me');
        }
        if (spot.booking_expired) {
          classes.push('booking-expired');
        }
      } 
      else if (spot.is_available) {
        classes.push('available');
        if (spot.vehicle_type === 'EV') {
          classes.push('ev-spot');
        }
      }

      if (this.selectedspot && this.selectedspot.id === spot.id) {
        classes.push('selected');
      }

      return classes;
    },

    getspoticon(spot) {
      if (spot.is_maintenance) return '🔧';
      if (spot.is_occupied) return '🚗';
      if (spot.is_booked) {
        if (spot.booked_by_current_user) {
          return '📅'; 
        }
        return '🔒'; 
      }
      if (spot.vehicle_type === 'EV') return '⚡';
      return '🅿️';
    },

    selspot(spot) {
      if (spot.is_occupied || spot.is_maintenance) return;

      if (spot.is_booked) {
        if (spot.booked_by_current_user) {
          this.selectedspot = spot;
          this.showoccupmodal = true;
        }
        return;
      }
      this.selectedspot = spot;
      this.showbookingmodal = true;
      this.vehnumerror = null;
      this.bookingdata = {
        vehicle_number: '',
        points_to_redeem: 0
      };
    },

    valvehnum(vehnum) {
      const pattern = /^[A-Z]{2}\d{2}[A-Z]\d{4}$/;
      return pattern.test(vehnum);
    },

    async confbooking() {
      this.vehnumerror = null;

      if (!this.bookingdata.vehicle_number.trim()) {
        this.vehnumerror = 'Vehicle number is required';
        return;
      }

      if (!this.valvehnum(this.bookingdata.vehicle_number)) {
        this.vehnumerror = 'Invalid format. Use: AB12C1234 (2 letters + 2 digits + 1 letter + 4 digits)';
        return;
      }

      try {
        const resp = await this.makeauthreq('/api/user/book-spot', {
          method: 'POST',
          body: JSON.stringify({
            spot_id: this.selectedspot.id,
            vehicle_number: this.bookingdata.vehicle_number,
            lot_name: this.selectedlot.name,
            points_to_redeem: this.bookingdata.points_to_redeem || 0
          })
        });

        if (resp && resp.ok) {
          const data = await resp.json();

          if (this.selectedspot) {
            this.selectedspot.status = 'B';
            this.selectedspot.is_booked = true;
            this.selectedspot.is_available = false;
            this.selectedspot.vehicle_number = this.bookingdata.vehicle_number;
            this.selectedspot.booking_id = data.booking_id;
            this.selectedspot.booking_expires_at = data.booking_expires_at;
            this.selectedspot.booked_by_current_user = true;
          }
          showToast.bookingSuccess(this.selectedspot.spot_number, this.selectedlot.name);
          this.clbookingmodal();
          await this.loaduserprof();
          await this.loadparkinglots();
          await this.viewlotspots(this.selectedlot);
        } 
        else if (resp) {
          const data = await resp.json();
          if (data.conflict_data) {
            this.vehconflictdata = data.conflict_data;
            this.showvehconflictmodal = true;
          } 
          else {
            alert(`❌ ${data.message || 'Booking failed'}`);
          }
        }
      } 
      catch (error) {
        console.error('Error booking spot:', error);
        alert('❌ Error booking spot');
      }
    },

    async confoccup() {
      this.vehnumerror = null;

      if (!this.bookingdata.vehicle_number.trim()) {
        this.vehnumerror = 'Vehicle number is required';
        return;
      }

      if (!this.valvehnum(this.bookingdata.vehicle_number)) {
        this.vehnumerror = 'Invalid format. Use: AB12C1234 (2 letters + 2 digits + 1 letter + 4 digits)';
        return;
      }

      try {
        const bookresp = await this.makeauthreq('/api/user/book-spot', {
          method: 'POST',
          body: JSON.stringify({
            spot_id: this.selectedspot.id,
            vehicle_number: this.bookingdata.vehicle_number,
            lot_name: this.selectedlot.name,
            points_to_redeem: this.bookingdata.points_to_redeem || 0
          })
        });

        if (bookresp && bookresp.ok) {
          const bookdata = await bookresp.json();
          const occupyresp = await this.makeauthreq('/api/user/occupy-spot', {
            method: 'POST',
            body: JSON.stringify({
              booking_id: bookdata.booking_id
            })
          });

          if (occupyresp && occupyresp.ok) {
            if (this.selectedspot) {
              this.selectedspot.status = 'O';
              this.selectedspot.is_occupied = true;
              this.selectedspot.is_available = false;
              this.selectedspot.is_booked = false;
              this.selectedspot.vehicle_number = this.bookingdata.vehicle_number;
            }

            alert('✅ Spot occupied successfully! Billing has started.');
            this.clbookingmodal();
            await this.loaduserprof();
            await this.loadparkinglots();
            await this.loadactres();
            await this.viewlotspots(this.selectedlot);
          } 
          else {
            const occupdata = await occupyresp.json();
            alert(`❌ Booking succeeded but occupancy failed: ${occupdata.message}`);
          }
        } 
        else if (bookresp) {
          const data = await bookresp.json();
          if (data.conflict_data) {
            this.vehconflictdata = data.conflict_data;
            this.showvehconflictmodal = true;
          }
           else {
            alert(`❌ ${data.message || 'Booking failed'}`);
          }
        }
      } 
      catch (error) {
        console.error('Error occupying spot:', error);
        alert('❌ Error occupying spot');
      }
    },

    clbookingmodal() {
      this.showbookingmodal = false;
      this.selectedspot = null;
      this.vehnumerror = null;
    },

    cloccupmodal() {
      this.showoccupmodal = false;
      this.selectedspot = null;
    },

    async cancbooking() {
      if (!this.selectedspot || !this.selectedspot.booking_id) {
        alert('❌ No booking found to cancel');
        return;
      }

      if (!confirm('🗑️ Are you sure you want to cancel this booking? This action cannot be undone.')) {
        return;
      }

      try {
        const resp = await this.makeauthreq('/api/user/cancel-booking', {
          method: 'POST',
          body: JSON.stringify({
            booking_id: this.selectedspot.booking_id
          })
        });

        if (resp && resp.ok) {
          if (this.selectedspot) {
            this.selectedspot.status = 'A';
            this.selectedspot.is_available = true;
            this.selectedspot.is_booked = false;
            this.selectedspot.booked_by_current_user = false;
            this.selectedspot.vehicle_number = null;
            this.selectedspot.booking_id = null;
            this.selectedspot.booking_expires_at = null;
          }

          alert('✅ Booking cancelled successfully!');
          this.cloccupmodal();
          await this.loaduserprof();
          await this.loadparkinglots();
          await this.viewlotspots(this.selectedlot);
        } 
        else if (resp) {
          const data = await resp.json();
          alert(`❌ ${data.message || 'Failed to cancel booking'}`);
        }
      } 
      catch (error) {
        console.error('Error cancelling booking:', error);
        alert('❌ Error cancelling booking');
      }
    },

    async confbkoccup(){
      if (!this.selectedspot || !this.selectedspot.booking_id) {
        alert('❌ Invalid booking information');
        return;
      }

      try {
        const resp = await this.makeauthreq('/api/user/occupy-spot', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({booking_id: this.selectedspot.booking_id})
        });

        if (resp && resp.ok) {
          const data = await resp.json();
          this.cloccupmodal();
          await this.loadparkinglots();
          await this.loadactres();
          if (this.selectedlot) {
            await this.viewlotspots(this.selectedlot);
          }

          alert(`✅ ${data.message}`);
        } 
        else {
          const errorData = await resp.json();
          alert(`❌ ${errorData.message}`);
        }
      } 
      catch (error) {
        console.error('Error occupying spot:', error);
        alert('❌ Error occupying spot');
      }
    },

    openrelmodal(res) {
      this.selectedres = res;
      this.showrelmodal = true;
    },

    async confrel() {
      try {
        const resp = await this.makeauthreq(`/api/user/release-spot/${this.selectedres.id}`, {method: 'POST'});

        if (resp && resp.ok) {
          const data = await resp.json();
          if (this.selectedres && this.lotSpots) {
            const relspot = this.lotSpots.find(spot =>
              spot.id === this.selectedres.spot_id
            );
            if (relspot) {
              relspot.status = 'A';
              relspot.is_occupied = false;
              relspot.vehicle_number = null;
            }
          }

          this.reldetails = data.release_details;
          this.showrelsucmodal = true;
          this.closerelmodal();
          await this.loaduserprof();
          await this.loadparkinglots();
          await this.loadactres();
          if (this.selectedlot) {
            await this.viewlotspots(this.selectedlot);
          }
        } 
        else if (resp) {
          const data = await resp.json();
          showToast.error(data.message || 'Release failed');
        }
      } 
      catch (error) {
        console.error('Error releasing spot:', error);
        alert('❌ Error releasing spot');
      }
    },

    closerelmodal() {
      this.showrelmodal = false;
      this.selectedres = null;
    },

    clrelsucmodal() {
      this.showrelsucmodal = false;
      this.reldetails = null;
    },

    clvehconflictmodal() {
      this.showvehconflictmodal = false;
      this.vehconflictdata = null;
    },

    formatdt(d) {
      return new Date(d).toLocaleString();
    },

    viewbooking(booking) {
      this.selectedlot = this.parkinglots.find(lot => lot.name === booking.location_name);
      if (this.selectedlot) {
        this.viewlotspots(this.selectedlot).then(() => {
          const spot = this.avspots.find(s => s.spot_number === booking.spot_number);
          if (spot) {
            this.selectedspot = spot;
            this.selectedspot.booking_id = booking.id;
            this.selectedspot.booking_expires_at = booking.expires_at;
            this.selectedspot.vehicle_number = booking.vehicle_number;
            this.showoccupmodal = true;
          }
        });
      }
    },

    calcdur(sttime) {
      const start = new Date(sttime);
      const now = new Date();
      const dtot = now - start;
      const dhr = Math.floor(dtot / (1000 * 60 * 60));
      const dmins = Math.floor((dtot % (1000 * 60 * 60)) / (1000 * 60));
      return `${dhr}h ${dmins}m`;
    },

    calcurrcost(res) {
      const start = new Date(res.parking_timestamp);
      const now = new Date();
      const dhr = (now - start) / (1000 * 60 * 60);
      const lot = this.parkinglots.find(l => l.name === res.prime_location_name);
      const perhr = lot.price_per_hour; 
      return dhr * perhr;
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

    gotoprof() {
      this.$router.push('/profile');
    },

    gotohist() {
      this.$router.push('/history');
    },

    gotofb() {
      this.$router.push('/feedback');
    },

    async createucharts() {
      const sessctx = document.getElementById('sessionchart');
      if (sessctx && this.reservations.length > 0) {
        const monthlydata = this.processmonthlydata(this.reservations, 'count');
        if (this.sessionchart) {
          this.sessionchart.destroy();
        }

        this.sessionchart = new Chart(sessctx, {
          type: 'line',
          data: {
            labels: monthlydata.labels,
            datasets: [{
              label: 'Parking Sessions',
              data: monthlydata.data,
              borderColor: '#ff6b6b',
              backgroundColor: 'rgba(255, 107, 107, 0.1)',
              tension: 0.4
            }]
          },
          options: {
            responsive: true,
            plugins: {
              legend: {
                display: false
              }
            },
            scales: {
              y: {
                beginAtZero: true,
                ticks: {
                  stepSize: 1
                }
              }
            }
          }
        });
      }

      const spendctx = document.getElementById('spendingchart');
      if (spendctx && this.reservations.length > 0) {
        const monthlydata = this.processmonthlydata(this.reservations, 'cost');
        if (this.spendingchart) {
          this.spendingchart.destroy();
        }

        this.spendingchart = new Chart(spendctx, {
          type: 'bar',
          data: {
            labels: monthlydata.labels,
            datasets: [{
              label: 'Monthly Spending ($)',
              data: monthlydata.data,
              backgroundColor: '#4ecdc4',
              borderColor: '#45b7aa',
              borderWidth: 1
            }]
          },
          options: {
            responsive: true,
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

    processmonthlydata(reservations, type) {
      const monthlystats = {};
      const now = new Date();

      for (let i = 5; i >= 0; i--) {
        const date = new Date(now.getFullYear(), now.getMonth() - i, 1);
        const key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
        monthlystats[key] = type === 'count' ? 0 : 0.0;
      }

      reservations.forEach(res => {
        const date = new Date(res.parking_timestamp);
        const key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;

        if (monthlystats.hasOwnProperty(key)) {
          if (type === 'count') {
            monthlystats[key]++;
          } else if (type === 'cost') {
            const cost = (typeof res.parking_cost === 'number') ? res.parking_cost : 0;
            monthlystats[key] += cost;
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
    }
  }
}
</script>
