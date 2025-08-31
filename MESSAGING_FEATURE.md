# Admin Panel Messaging Feature

## Overview
A new messaging section has been added to the admin panel that allows administrators to send messages to all users or active users only.

## Features

### 1. Message Composition
- **Title**: Add a descriptive title for the message
- **Message Text**: Write the main content with HTML formatting support
- **Message Type**: Choose from different categories:
  - 📢 Announcement
  - 🔄 Update
  - 🎁 Promotion
  - 🔧 Maintenance
  - 📝 Other

### 2. User Targeting
- **All Users**: Send to every registered user
- **Active Users Only**: Send only to users who have been active in the last 7 days (created account or made transactions)

### 3. Message Formatting
The system supports HTML formatting tags:
- `<b>Bold text</b>`
- `<i>Italic text</i>`
- `<code>Code text</code>`

### 4. Delivery Statistics
After sending, the admin panel shows:
- Number of successfully sent messages
- Number of failed deliveries
- Total time taken for delivery

## Technical Implementation

### Backend Routes
- `GET /messages` - Messaging page
- `POST /send_message_to_all` - API endpoint for sending messages

### Database Integration
- Uses existing User and Transaction tables
- Active users are determined by:
  - Users created in the last 7 days
  - Users who made transactions in the last 7 days

### Rate Limiting
- Messages are sent with rate limiting (50 messages per second) to avoid Telegram API limits
- Progress tracking with real-time feedback

### Error Handling
- Graceful handling of failed message deliveries
- Detailed error reporting
- User-friendly error messages

## Usage Instructions

1. **Access the Messaging Section**
   - Navigate to the admin panel
   - Click on "Xabarlar" in the navigation menu

2. **Compose Your Message**
   - Enter a title for the message
   - Write the message content
   - Select the appropriate message type
   - Choose whether to send to all users or active users only

3. **Send the Message**
   - Click "Xabar yuborish" button
   - Wait for the delivery process to complete
   - Review the delivery statistics

## Security Features
- Admin-only access (requires admin ID in config)
- Form validation and sanitization
- Rate limiting to prevent abuse
- Comprehensive error logging

## Future Enhancements
- Scheduled message sending
- Message templates
- User segmentation (by activity level, balance, etc.)
- Message history and analytics
- Rich media support (images, documents)
