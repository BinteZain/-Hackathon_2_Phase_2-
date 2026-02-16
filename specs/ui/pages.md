# UI Pages Specification

## Overview
This document outlines the main pages of the Hackathon-Todo application and their purposes.

## Public Pages

### 1. Landing Page (`/`)
- Hero section with app description
- Key features highlights
- Call-to-action buttons (Sign Up, Learn More)
- Testimonials or user statistics
- Footer with links

### 2. Login Page (`/login`)
- Email and password inputs
- "Remember me" checkbox
- Forgot password link
- Sign up link
- Social login options (optional)

### 3. Registration Page (`/register`)
- First name, last name inputs
- Email and password inputs
- Password confirmation
- Terms and conditions agreement
- Login link
- Social registration options (optional)

### 4. Forgot Password Page (`/forgot-password`)
- Email input field
- Instructions for password reset
- Back to login link

### 5. Reset Password Page (`/reset-password/:token`)
- New password input
- Password confirmation
- Token validation

## Protected Pages (require authentication)

### 6. Dashboard (`/dashboard`)
- Welcome message with user name
- Summary of tasks (total, pending, completed)
- Quick stats and charts
- Recent activity feed
- Quick task creation form

### 7. Tasks List (`/tasks`)
- Filter controls (by status, priority, date)
- Search functionality
- Sort options
- Task cards displaying all tasks
- Pagination controls
- Empty state when no tasks exist
- Floating action button for creating new tasks

### 8. Task Detail (`/tasks/:id`)
- Detailed view of a single task
- Edit functionality
- Related tasks suggestions
- Activity history (optional)

### 9. Task Creation (`/tasks/new`)
- Form for creating a new task
- All required fields for task creation
- Validation feedback
- Auto-save functionality (optional)

### 10. Task Editing (`/tasks/:id/edit`)
- Form for editing an existing task
- Pre-filled with existing task data
- Validation feedback

### 11. Profile Page (`/profile`)
- User information display
- Avatar upload
- Personal details editing
- Password change form
- Account settings
- Notification preferences

### 12. Settings Page (`/settings`)
- Application preferences
- Theme selection (light/dark mode)
- Notification settings
- Connected applications (optional)
- Account deletion option (with confirmation)

## Shared Elements Across Pages

### Global Header
- Logo linking to dashboard
- Navigation menu
- User profile dropdown
- Notification bell (if notifications are implemented)

### Global Sidebar (on larger screens)
- Navigation links to main sections
- Collapsible for smaller screens
- User profile information

### Mobile Navigation
- Bottom tab bar for main navigation
- Hamburger menu for additional options

## Responsive Behavior
- All pages must be fully responsive
- Mobile-first design approach
- Appropriate touch targets for mobile users
- Optimized layouts for tablet and desktop