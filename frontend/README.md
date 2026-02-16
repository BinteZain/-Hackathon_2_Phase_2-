# Hackathon-Todo Frontend

This is the frontend application for the Hackathon-Todo project, built with Next.js 16+ and Tailwind CSS.

## Features

- **Authentication**: Login/signup pages with Better Auth integration
- **Task Management**: Full CRUD operations for tasks
- **Responsive UI**: Works on desktop, tablet, and mobile devices
- **Professional UI Components**: TaskCard and TaskForm components
- **API Integration**: Axios client with JWT token handling
- **Error Handling**: Proper error states and notifications
- **Loading States**: Visual feedback during API operations

## Pages

- `/` - Landing page with app introduction
- `/login` - User login/signup page
- `/tasks` - Task management page with list and form

## Components

- `TaskCard` - Professional UI for displaying task information
- `TaskForm` - Form for creating and updating tasks

## API Client

The application uses an API client in `src/lib/api.ts` that:
- Attaches JWT tokens to the Authorization header
- Handles common error cases
- Provides a base URL for API requests

## Environment Variables

Create a `.env.local` file with the following variables:

```env
NEXT_PUBLIC_API_URL=http://localhost:4000/api/v1
```

## Running the Application

1. Install dependencies:
   ```bash
   npm install
   ```

2. Run the development server:
   ```bash
   npm run dev
   ```

3. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Building for Production

To build the application for production:

```bash
npm run build
```

Then run the production server:

```bash
npm start
```

## Project Structure

```
src/
├── pages/           # Next.js pages
├── components/      # Reusable UI components
├── lib/            # Utilities and API client
├── contexts/       # React context providers
├── types/          # TypeScript type definitions
└── styles/         # Global styles
```