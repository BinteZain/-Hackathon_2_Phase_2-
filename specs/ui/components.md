# UI Components Specification

## Overview
This document outlines the reusable UI components for the Hackathon-Todo application.

## Core Components

### 1. Layout Components
- **AppContainer** - Main layout wrapper with consistent padding and max-width
- **Header** - Navigation bar with logo, navigation links, and user menu
- **Sidebar** - Collapsible sidebar for navigation on larger screens
- **Footer** - Site footer with copyright and links

### 2. Form Components
- **InputField** - Standard text input with validation states
- **TextArea** - Multi-line text input
- **Select** - Dropdown selection component
- **Checkbox** - Checkbox with label
- **Button** - Various button styles (primary, secondary, danger, etc.)
- **Form** - Wrapper for forms with validation support

### 3. Task-Specific Components
- **TaskCard** - Display individual task with title, description, status, and actions
- **TaskList** - Container for multiple TaskCards with filtering options
- **TaskModal** - Modal form for creating/editing tasks
- **TaskStatusBadge** - Visual indicator for task status
- **PrioritySelector** - Component for selecting task priority

### 4. Authentication Components
- **LoginForm** - Form for user login
- **RegisterForm** - Form for user registration
- **ForgotPasswordForm** - Form for initiating password reset
- **ResetPasswordForm** - Form for completing password reset
- **UserProfile** - Component to display and edit user profile

### 5. Navigation Components
- **Breadcrumb** - Navigation trail showing current location
- **Pagination** - Component for navigating through pages of data
- **TabBar** - Horizontal tabs for switching between views

### 6. Feedback Components
- **Alert** - Notification messages (success, error, warning, info)
- **Spinner** - Loading indicator
- **ProgressBar** - Progress visualization
- **Tooltip** - Hover information display

### 7. Utility Components
- **Icon** - SVG icon component with various built-in icons
- **Avatar** - User profile picture display
- **EmptyState** - Placeholder for empty data views
- **SearchBox** - Search input with clear functionality

## Component Props Convention
- All components should accept a `className` prop for additional styling
- Boolean props should follow the `is` prefix (e.g., `isVisible`, `isDisabled`)
- Event handlers should follow the `on` prefix (e.g., `onClick`, `onChange`)
- Components should be designed to be responsive by default

## Styling Approach
- Use utility-first CSS framework (e.g., Tailwind CSS)
- Consistent color palette defined in theme variables
- Responsive breakpoints: sm (640px), md (768px), lg (1024px), xl (1280px)
- Consistent spacing using a scale (e.g., 0, 0.5, 1, 1.5, 2, 2.5, 3, ...)