# Food Delivery App - User Manual

## Table of Contents
1. [Getting Started](#getting-started)
2. [Customer Guide](#customer-guide)
3. [Delivery Partner Guide](#delivery-partner-guide)
4. [Administrator Guide](#administrator-guide)
5. [Troubleshooting](#troubleshooting)

---

## Getting Started

### System Requirements
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection
- Mobile number for registration

### Accessing the Application
- **Website URL**: `http://localhost:8000` (or your deployed URL)
- **Customer Login**: `/login/`
- **Delivery Partner Login**: `/login/`
- **Admin Login**: `/admin-login/`

---

## Customer Guide

### 1. Registration & Login

#### Sign Up (New Customer)
1. Visit the website and click **"Sign Up"**
2. Enter your mobile number
3. Enter your email address (optional)
4. Create a strong password
5. Enter your first and last name
6. Click **"Sign Up"**
7. You'll be redirected to the login page

#### Login
1. Go to `/login/`
2. Enter your mobile number or email
3. Enter your password
4. Click **"Login"**

### 2. Creating a Booking

#### Step-by-Step Process
1. From your dashboard, click **"Create Booking"**
2. Fill in the booking form:
   - **Pickup Address**: Enter the restaurant or pickup location address
   - **Delivery Address**: Enter your delivery address
   - **Customer Notes** (Optional): Add special instructions like:
     - Gate code or building number
     - Floor number
     - Contact preferences
     - Delivery instructions
3. Click **"Create Booking"**
4. Your booking will be created with status **"Pending"**

### 3. Tracking Your Booking

#### Booking Statuses
- **Pending**: Waiting for admin to assign a delivery partner
- **Assigned**: Delivery partner has been assigned
- **Started**: Delivery partner is on the way to pickup location
- **Reached**: Delivery partner has arrived at pickup location
- **Collected**: Order has been picked up
- **Delivered**: Order has been delivered to you
- **Cancelled**: Booking has been cancelled

#### View Booking Details
1. Go to **"My Bookings"** from the sidebar
2. Click on any booking to view details
3. You can see:
   - Pickup and delivery addresses
   - Your notes
   - Current status
   - Delivery partner information (once assigned)
   - Status history timeline

### 4. Chatting with Delivery Partner

#### When Chat is Available
- Chat becomes available once a delivery partner is assigned
- Chat is active during: Assigned, Started, Reached, and Collected statuses

#### How to Chat
1. Open your booking details
2. Scroll to the **"Chat with Delivery Partner"** section
3. Type your message in the text box
4. Click **"Send"** or press Enter
5. Messages appear in real-time

#### Chat Tips
- Be polite and clear
- Provide additional directions if needed
- Confirm delivery location details
- Ask for updates on delivery status

### 5. Cancelling a Booking

#### When You Can Cancel
- Only bookings in **"Pending"** or **"Assigned"** status can be cancelled
- Once delivery has started, cancellation is not allowed

#### How to Cancel
1. Open the booking details
2. Click **"Cancel Booking"** button
3. Enter a cancellation reason
4. Click **"Cancel Booking"** to confirm
5. Booking status will change to **"Cancelled"**

### 6. Managing Your Profile

#### Update Profile Information
1. Click on your name in the top-right corner
2. Select **"Profile"**
3. Update your information:
   - First name and last name
   - Email address
   - Address
   - Profile picture
4. Click **"Update Profile"**

---

## Delivery Partner Guide

### 1. Registration & Login

#### Sign Up (New Delivery Partner)
1. Visit `/delivery-signup/`
2. Enter your mobile number
3. Enter your email address (optional)
4. Create a password
5. Enter your first and last name
6. Click **"Sign Up"**
7. Wait for admin approval (if required)

#### Login
1. Go to `/login/`
2. Enter your mobile number or email
3. Enter your password
4. Click **"Login"**

### 2. Viewing Assigned Deliveries

#### Dashboard Overview
- View total deliveries assigned to you
- See active deliveries
- Check completed deliveries
- Today's delivery count

#### Delivery List
1. Click **"My Deliveries"** from the sidebar
2. View all your assigned deliveries
3. Filter by status if needed
4. Click on any delivery to view details

### 3. Managing Deliveries

#### Delivery Details
Each delivery shows:
- Customer information (name, phone)
- Pickup address
- Delivery address
- Customer notes (important instructions)
- Current status
- Status history

#### Updating Delivery Status

**Status Flow**:
1. **Assigned** → Click "Started" when you begin heading to pickup
2. **Started** → Click "Reached" when you arrive at pickup location
3. **Reached** → Click "Collected" after picking up the order
4. **Collected** → Click "Delivered" after delivering to customer

**How to Update**:
1. Open the delivery details
2. Select the new status from the dropdown
3. Add notes (optional) - e.g., "Customer not available, left at door"
4. Click **"Update Status"**

### 4. Communicating with Customers

#### Chat Feature
1. Open the delivery details
2. Scroll to **"Chat with Customer"** section
3. Type your message
4. Click **"Send"**

#### Communication Tips
- Notify customer when you start the delivery
- Update if there are any delays
- Confirm delivery location before arriving
- Be professional and courteous

#### Call Customer
- Click **"Call Customer"** button to directly call the customer's mobile number
- Use this for urgent clarifications

### 5. Best Practices

#### Before Starting Delivery
- Check pickup and delivery addresses
- Read customer notes carefully
- Verify you have the correct order

#### During Delivery
- Update status promptly at each stage
- Keep customer informed via chat
- Follow traffic rules and safety guidelines
- Handle food items with care

#### After Delivery
- Mark as "Delivered" immediately
- Confirm with customer if needed
- Take photo proof if required by policy

---

## Administrator Guide

### 1. Login

#### Admin Access
1. Go to `/admin-login/`
2. Enter your admin email
3. Enter your password
4. Click **"Login"**

### 2. Dashboard Overview

#### Key Metrics
- Total bookings
- Pending bookings (need assignment)
- Active bookings (in progress)
- Completed bookings
- Cancelled bookings
- User statistics (customers, delivery partners, admins)
- Today's statistics

### 3. Managing Bookings

#### View All Bookings
1. Click **"All Bookings"** from the sidebar
2. Use filters to find specific bookings:
   - Filter by status
   - Search by booking ID or mobile number
3. Click on any booking to view details

#### Assigning Delivery Partners

**When to Assign**:
- Bookings in "Pending" status need assignment
- You can reassign if needed

**How to Assign**:
1. Open the booking details
2. Scroll to **"Assign Delivery Partner"** section
3. Select a delivery partner from the dropdown
4. Click **"Assign Booking"**
5. Delivery partner will be notified

**Reassigning**:
- Follow the same process
- Select a different delivery partner
- Previous assignment will be updated

### 4. Managing Users

#### View Users
1. Click **"Users"** from the sidebar
2. Filter by role:
   - All users
   - Customers
   - Delivery partners
   - Admins
3. Search by mobile number or name

#### User Details
- Click on any user to view:
  - Profile information
  - Recent bookings/deliveries
  - Activity history

### 5. Reports & Analytics

#### Accessing Reports
1. Click **"Reports"** from the sidebar
2. Select date range (optional)
3. View statistics:
   - Total bookings in period
   - Completion rate
   - Cancellation rate
   - Top delivery partners
   - Top customers

#### Export Data
- Use browser print function (Ctrl+P) to save reports as PDF

### 6. Best Practices

#### Booking Management
- Assign delivery partners promptly to pending bookings
- Monitor active deliveries for delays
- Review cancellation reasons to improve service

#### Delivery Partner Management
- Distribute deliveries evenly
- Monitor delivery partner performance
- Address customer complaints quickly

#### Customer Service
- Respond to issues promptly
- Review customer notes for special requirements
- Track delivery success rates

---

## Troubleshooting

### Common Issues

#### Cannot Login
**Problem**: "Invalid credentials" error
**Solution**:
- Verify mobile number/email is correct
- Check password (case-sensitive)
- Use "Forgot Password" if needed
- Contact admin if account is locked

#### Booking Not Showing
**Problem**: Created booking doesn't appear
**Solution**:
- Refresh the page (Ctrl+R or F5)
- Check "All Bookings" section
- Verify you're logged in with correct account

#### Chat Not Working
**Problem**: Cannot send messages
**Solution**:
- Ensure booking has assigned delivery partner
- Check booking status (chat only works for active deliveries)
- Refresh the page
- Check internet connection

#### Customer Notes Disappearing
**Problem**: Notes not visible after some time
**Solution**:
- Clear browser cache (Ctrl+Shift+R)
- Notes are saved in database, refresh to see them
- Contact admin if issue persists

#### Status Not Updating
**Problem**: Delivery status doesn't change
**Solution**:
- Refresh the page
- Check if you have permission to update
- Verify correct status transition
- Contact admin if blocked

### Browser Issues

#### Recommended Browsers
- Google Chrome (latest version)
- Mozilla Firefox (latest version)
- Safari (latest version)
- Microsoft Edge (latest version)

#### Clear Browser Cache
- **Chrome/Edge**: Ctrl+Shift+Delete
- **Firefox**: Ctrl+Shift+Delete
- **Safari**: Cmd+Option+E

### Getting Help

#### Contact Support
- Email: support@fooddeliveryapp.com (if configured)
- Phone: Contact your system administrator
- In-app: Use the help section

#### Report a Bug
1. Note the exact error message
2. Take a screenshot if possible
3. Note what you were doing when error occurred
4. Contact administrator with details

---

## Tips for Best Experience

### For Customers
- Provide clear delivery addresses
- Add detailed notes for complex locations
- Keep phone accessible during delivery
- Rate delivery partners (if feature available)

### For Delivery Partners
- Keep app open during deliveries
- Update status promptly
- Communicate proactively with customers
- Maintain professional conduct

### For Administrators
- Monitor pending bookings regularly
- Assign deliveries based on partner availability
- Review reports to identify trends
- Address issues quickly

---

## Security & Privacy

### Account Security
- Use strong passwords (8+ characters, mix of letters, numbers, symbols)
- Don't share your login credentials
- Log out after using shared devices
- Change password regularly

### Privacy
- Your personal information is protected
- Phone numbers are only visible to relevant parties
- Chat messages are private between customer and delivery partner
- Admins can view data for support purposes only

### Data Protection
- All data is encrypted in transit
- Passwords are securely hashed
- Regular backups are maintained
- Comply with data protection regulations

---

## Frequently Asked Questions (FAQ)

### General

**Q: Is registration free?**
A: Yes, registration is free for both customers and delivery partners.

**Q: Can I use the app without a mobile number?**
A: No, a mobile number is required for registration and communication.

**Q: How do I change my password?**
A: Go to your profile settings and use the "Change Password" option.

### For Customers

**Q: How long does it take to get a delivery partner assigned?**
A: Usually within a few minutes, depending on availability.

**Q: Can I cancel after delivery has started?**
A: No, cancellation is only allowed for pending or assigned bookings.

**Q: Can I track my delivery in real-time?**
A: You can see status updates and chat with the delivery partner for updates.

### For Delivery Partners

**Q: How do I get assigned deliveries?**
A: Admins assign deliveries based on availability and location.

**Q: Can I reject a delivery?**
A: Contact admin if you cannot complete an assigned delivery.

**Q: What if customer is not available?**
A: Try calling, wait for a reasonable time, then contact admin.

### For Administrators

**Q: Can I delete bookings?**
A: Bookings should not be deleted for record-keeping. Mark as cancelled instead.

**Q: How do I add new delivery partners?**
A: Delivery partners self-register, or you can create accounts manually.

**Q: Can I see chat messages?**
A: Admins can view chat logs for support and quality purposes.

---

## Glossary

- **Booking**: An order for food delivery
- **Pickup Address**: Location where delivery partner collects the order
- **Delivery Address**: Location where order is delivered to customer
- **Status**: Current state of the booking in the delivery process
- **Assignment**: Linking a delivery partner to a booking
- **Chat**: Real-time messaging between customer and delivery partner
- **Dashboard**: Main overview page after login
- **Profile**: User account information and settings

---

## Version Information

- **Application Version**: 1.0
- **Last Updated**: 2025
- **Manual Version**: 1.0

---
