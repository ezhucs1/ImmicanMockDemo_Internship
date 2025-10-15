# 👥 immiCan User Guide

## **Overview**
The immiCan platform connects immigrants (clients) with certified service providers for Canadian immigration services. This comprehensive guide covers both client and service provider functionalities.

## **User Types**

### **👤 Clients (Immigrants)**
- **Purpose**: Find and connect with service providers
- **Features**: Service requests, provider search, messaging, rating system
- **Registration**: http://localhost:5173/register
- **Login**: http://localhost:5173/login
- **Dashboard**: http://localhost:5173/dashboard

### **🏢 Service Providers**
- **Purpose**: Offer services to immigrants
- **Features**: Request management, client communication, service completion
- **Registration**: http://localhost:5173/service-provider-register
- **Login**: http://localhost:5173/service-provider-login
- **Dashboard**: http://localhost:5173/service-provider-dashboard

---

## **👤 CLIENT (IMMIGRANT) GUIDE**

### **Getting Started**

#### **Account Registration**
1. **Visit Registration Page**: http://localhost:5173/register
2. **Fill Registration Form**:
   - **Email**: Your email address (used for login)
   - **Full Name**: Your complete name
   - **Password**: Strong password (minimum 8 characters with uppercase, lowercase, numbers, and special characters)
3. **Create Account**: Click "Create Account" button
4. **Email Verification**: 
   - Verification email is sent automatically (check console for URL in development)
   - Click verification link or use manual verification: `./verify_email.sh your@email.com`
   - **Important**: You must verify your email before you can login

#### **Login Process**
1. **Visit Login Page**: http://localhost:5173/login
2. **Enter Credentials**: Email and password
3. **Sign In**: Click "Sign in" button
4. **Dashboard Access**: Redirected to client dashboard

**Important Security Note**: 
- Clients can ONLY login through the client login page
- Service providers can ONLY login through the service provider login page
- Cross-login attempts are blocked for security

### **Client Dashboard Features**

#### **Welcome Section**
- **Personalized Greeting**: "Welcome, [Your First Name]"
- **Account Information**: Profile details
- **Quick Actions**: Access to main features

#### **Service Provider Directory**
- **Browse Providers**: View all available service providers
- **Filter by Service Type**: Legal, Financial, Settlement, Employment, Education
- **Provider Profiles**: Ratings, reviews, and service descriptions
- **Contact Providers**: Direct communication options

#### **Your Service Requests**
- **Active Requests**: All submitted service requests
- **Request Status**: Pending, Accepted, In Progress, Completed, Confirmed
- **Priority Levels**: High, Medium, Low (displayed as "Priority: High")
- **Action Buttons**: View details, communicate, rate service

#### **Request Service Feature**
- **Service Type Selection**: Choose from available categories
- **Priority Setting**: Set urgency level (High, Medium, Low)
- **Detailed Description**: Provide specific requirements
- **Submit Request**: Send request to available providers

### **Service Request Workflow**

#### **1. Creating a Service Request**
1. **Click "Request Service"**: Available on dashboard
2. **Select Service Type**: Choose from dropdown menu
3. **Set Priority Level**: High, Medium, or Low
4. **Enter Title**: Brief description of your need
5. **Provide Description**: Detailed explanation of requirements
6. **Submit Request**: Click "Submit Request" button

#### **2. Request Status Tracking**
- **Pending**: Request submitted, waiting for provider acceptance
- **Accepted**: Provider has accepted your request
- **In Progress**: Service is being provided
- **Completed**: Service has been completed by provider
- **Confirmed**: You have confirmed and rated the service

#### **3. Communication with Providers**
- **Real-Time Messaging**: Chat directly with service provider
- **Message History**: All conversations are saved
- **File Sharing**: Share documents if needed
- **Notification System**: Get notified of new messages

#### **4. Service Completion Process**
1. **Provider Completes Service**: Provider marks service as completed
2. **Review Service**: You receive notification to review the service
3. **Rate Provider**: Give 1-5 star rating
4. **Confirm Completion**: Confirm that service met your expectations
5. **Request Closure**: Request is closed and removed from active list

### **Client Communication Features**

#### **Real-Time Messaging**
- **Instant Communication**: Chat with providers in real-time
- **Message Notifications**: Get notified of new messages
- **Conversation History**: All messages are saved and accessible
- **Read Receipts**: See when messages are read

#### **Message Features**
- **Text Messages**: Send and receive text messages
- **Emoji Support**: Use emojis in messages
- **Message Status**: See sent, delivered, and read status
- **Conversation Management**: Organize conversations by service request

### **Client Rating and Review System**

#### **Provider Rating**
- **5-Star Rating**: Rate providers from 1 to 5 stars
- **Rating Criteria**: Based on service quality, communication, and professionalism
- **Public Ratings**: Your ratings help other clients choose providers
- **Rating History**: View your previous ratings

#### **Review Process**
1. **Service Completion**: Provider marks service as completed
2. **Rating Prompt**: You receive notification to rate the service
3. **Star Rating**: Select 1-5 stars
4. **Optional Feedback**: Provide written feedback
5. **Submit Rating**: Confirm your rating and feedback

---

## **🏢 SERVICE PROVIDER GUIDE**

### **Getting Started**

#### **Account Registration**
1. **Visit Registration Page**: http://localhost:5173/service-provider-register
2. **Fill Registration Form**:
   - **Email**: Your business email address
   - **First Name**: Your first name
   - **Last Name**: Your last name
   - **Business Name**: Your service provider business name
   - **Service Type**: Choose from Legal, Financial, Settlement, Employment, Education
   - **Description**: Brief description of your services
   - **Password**: Strong password (minimum 8 characters with complexity requirements)
3. **Create Account**: Click "Register as Service Provider" button
4. **Email Verification**: 
   - Verification email is sent automatically (check console for URL in development)
   - Click verification link or use manual verification: `./verify_email.sh your@email.com`
   - **Important**: You must verify your email before you can login

#### **Login Process**
1. **Visit Login Page**: http://localhost:5173/service-provider-login
2. **Enter Credentials**: Email and password
3. **Sign In**: Click "Sign in" button
4. **Dashboard Access**: Redirected to service provider dashboard

**Important Security Note**: 
- Service providers can ONLY login through the service provider login page
- Clients can ONLY login through the client login page
- Cross-login attempts are blocked for security

### **Service Provider Dashboard Features**

#### **Welcome Section**
- **Personalized Greeting**: "Welcome, [Your First Name]"
- **Business Information**: Your service provider profile
- **Quick Stats**: Number of requests, active conversations, ratings

#### **Incoming Service Requests**
- **Request List**: All pending service requests from clients
- **Request Details**: Title, description, priority, client information
- **Action Buttons**: Accept request, view details
- **Request Status**: Pending, Accepted, In Progress, Completed

#### **Active Conversations**
- **Conversation List**: All active conversations with clients
- **Message Previews**: Latest message from each conversation
- **Unread Messages**: Notification of unread messages
- **Quick Access**: Direct access to conversation interface

#### **Service Management**
- **Completed Services**: History of completed services
- **Client Ratings**: Ratings received from clients
- **Service Statistics**: Performance metrics and analytics
- **Profile Management**: Update business information

### **Service Provider Workflow**

#### **1. Receiving Service Requests**
1. **Request Notification**: New requests appear in dashboard
2. **Review Request**: Read client's requirements and details
3. **Assess Feasibility**: Determine if you can provide the service
4. **Make Decision**: Accept or decline the request

#### **2. Accepting Service Requests**
1. **Click "Accept Request"**: Available for pending requests
2. **Confirmation**: Confirm acceptance of the request
3. **Conversation Creation**: Automatic conversation creation with client
4. **Client Notification**: Client is notified of acceptance

#### **3. Providing Services**
1. **Client Communication**: Use messaging system to communicate
2. **Service Delivery**: Provide the requested service
3. **Progress Updates**: Keep client informed of progress
4. **Service Completion**: Mark service as completed when finished

#### **4. Service Completion Process**
1. **Mark as Completed**: Click "Mark as Completed" button
2. **Add Completion Notes**: Optional notes about the service provided
3. **Client Notification**: Client is notified to review and rate
4. **Wait for Confirmation**: Client confirms completion and provides rating
5. **Request Closure**: Request is closed after client confirmation

### **Service Provider Communication Features**

#### **Real-Time Messaging**
- **Instant Communication**: Chat with clients in real-time
- **Message Notifications**: Get notified of new messages
- **Conversation History**: All messages are saved and accessible
- **Read Receipts**: See when messages are read

#### **Message Features**
- **Text Messages**: Send and receive text messages
- **Professional Communication**: Maintain professional tone
- **Message Status**: See sent, delivered, and read status
- **Conversation Management**: Organize conversations by service request

### **Service Provider Rating System**

#### **Receiving Ratings**
- **Client Ratings**: Receive 1-5 star ratings from clients
- **Rating Display**: Ratings are displayed on your profile
- **Rating History**: View all ratings received
- **Rating Impact**: Ratings affect your visibility to clients

#### **Rating Management**
- **Profile Visibility**: Higher ratings improve profile visibility
- **Client Trust**: Good ratings build client trust
- **Service Quality**: Use ratings to improve service quality
- **Professional Reputation**: Maintain professional reputation

---

## **🔄 PLATFORM WORKFLOWS**

### **Complete Service Request Workflow**

#### **Step 1: Client Creates Request**
1. Client logs into dashboard
2. Clicks "Request Service"
3. Fills out service request form
4. Submits request to platform

#### **Step 2: Provider Receives Request**
1. Provider logs into dashboard
2. Sees new request in "Incoming Requests"
3. Reviews request details
4. Decides to accept or decline

#### **Step 3: Request Acceptance**
1. Provider clicks "Accept Request"
2. System creates conversation between client and provider
3. Client is notified of acceptance
4. Both parties can now communicate

#### **Step 4: Service Delivery**
1. Provider and client communicate via messaging
2. Provider delivers the requested service
3. Client receives service and provides feedback
4. Provider marks service as completed

#### **Step 5: Service Completion**
1. Provider marks service as completed
2. Client receives notification to review service
3. Client rates provider (1-5 stars)
4. Client confirms service completion
5. Request is closed and removed from active lists

### **Communication Workflow**

#### **Real-Time Messaging Process**
1. **Conversation Access**: Both parties access conversation interface
2. **Message Sending**: Send messages in real-time
3. **Message Delivery**: Messages are delivered instantly
4. **Message Storage**: All messages are saved to database
5. **Message Notifications**: Parties are notified of new messages

#### **Message Features**
- **Real-Time Updates**: Messages appear instantly
- **Message History**: All messages are preserved
- **Read Receipts**: See when messages are read
- **Unread Indicators**: Visual indicators for unread messages

---

## **🛡️ SECURITY FEATURES**

### **Account Security**
- **Strong Password Requirements**: Minimum 8 characters with complexity
- **JWT Authentication**: Secure token-based authentication
- **Session Management**: Automatic logout for security
- **Password Recovery**: Reset password via email

### **Data Protection**
- **Encrypted Communication**: All messages are encrypted
- **Secure Storage**: Personal data is securely stored
- **Privacy Controls**: Control what information is shared
- **Data Export**: Request your data export

### **Platform Security**
- **Input Validation**: All inputs are validated and sanitized
- **Rate Limiting**: Prevents abuse and spam
- **Security Monitoring**: All activities are logged
- **Audit Trails**: Complete activity tracking

---

## **🌐 PLATFORM FEATURES**

### **Multilingual Support**
- **Language Options**: English, French, Spanish, Chinese
- **Interface Translation**: All interface elements translated
- **Content Translation**: Service descriptions and messages
- **Language Switching**: Change language anytime

### **Mobile Responsiveness**
- **Mobile Friendly**: Works on all mobile devices
- **Touch Interface**: Optimized for touch screens
- **Responsive Design**: Adapts to different screen sizes
- **Mobile Notifications**: Get notifications on mobile devices

### **Accessibility Features**
- **Screen Reader Support**: Compatible with screen readers
- **Keyboard Navigation**: Full keyboard accessibility
- **High Contrast**: High contrast mode available
- **Font Size Options**: Adjustable font sizes

---

## **🔧 TROUBLESHOOTING**

### **Common Issues**

#### **Login Problems**
- **Forgot Password**: Use "Forgot Password" link
- **Account Locked**: Contact support if account is locked
- **Email Not Recognized**: Verify email address spelling
- **Password Not Working**: Check caps lock and special characters

#### **Service Request Issues**
- **Request Not Submitted**: Check all required fields
- **No Provider Response**: Wait 24-48 hours, then contact support
- **Request Status Not Updating**: Refresh page or contact support
- **Cannot Communicate**: Check if request is accepted

#### **Messaging Issues**
- **Messages Not Sending**: Check internet connection
- **Messages Not Receiving**: Refresh page or check notifications
- **Conversation Not Loading**: Clear browser cache
- **Real-Time Not Working**: Check WebSocket connection

### **Getting Help**
- **Help Center**: Access help documentation
- **Contact Support**: Email support for assistance
- **FAQ Section**: Common questions and answers
- **Video Tutorials**: Step-by-step video guides

---

## **📋 BEST PRACTICES**

### **For Clients**
- **Be Specific**: Provide detailed descriptions of your needs
- **Set Realistic Priorities**: Use appropriate priority levels
- **Include Timeline**: Mention your preferred timeline
- **Ask Questions**: Clarify any doubts with providers
- **Be Professional**: Maintain professional communication
- **Be Responsive**: Reply to messages promptly
- **Rate Honestly**: Provide accurate ratings based on experience

### **For Service Providers**
- **Respond Promptly**: Reply to requests and messages quickly
- **Be Professional**: Maintain professional communication
- **Provide Quality Service**: Deliver high-quality services
- **Communicate Clearly**: Keep clients informed of progress
- **Complete Services**: Mark services as completed when finished
- **Maintain Ratings**: Work to maintain good client ratings
- **Update Profile**: Keep business information current

---

## **📞 SUPPORT AND RESOURCES**

### **Help Resources**
- **User Guide**: This comprehensive guide
- **Video Tutorials**: Step-by-step video instructions
- **FAQ Section**: Frequently asked questions
- **Contact Support**: Direct support contact

### **Community Resources**
- **User Forums**: Connect with other users
- **Success Stories**: Read about successful immigration stories
- **Tips and Advice**: Get tips from experienced users
- **News and Updates**: Stay updated with platform news

### **Legal and Compliance**
- **Terms of Service**: Platform terms and conditions
- **Privacy Policy**: Data protection and privacy policy
- **User Agreement**: User responsibilities and rights
- **Complaint Process**: How to file complaints or concerns

---

## **🚀 GETTING STARTED**

### **Quick Demo (Pre-created Accounts)**
```bash
# Show demo user credentials
./show_demo_users.sh
```

**Demo Accounts Available:**
- **Client**: `client@example.com` / `ClientPass123!`
- **Service Provider**: `provider@example.com` / `ProviderPass123!`
- **Additional Users**: See `./show_demo_users.sh` for complete list

### **For Clients**
1. **Login**: Use demo account or register new account
2. **Access Dashboard**: http://localhost:5173/dashboard
3. **Browse Providers**: Find suitable service providers
4. **Request Services**: Submit service requests
5. **Communicate**: Chat with providers
6. **Rate Services**: Provide feedback after service completion

### **For Service Providers**
1. **Login**: Use demo account or register new account
2. **Access Dashboard**: http://localhost:5173/service-provider-dashboard
3. **View Requests**: Review incoming service requests
4. **Accept Requests**: Accept suitable requests
5. **Provide Services**: Deliver requested services
6. **Complete Services**: Mark services as completed

---

**Need help? Contact our support team or visit our help center for additional assistance.**
