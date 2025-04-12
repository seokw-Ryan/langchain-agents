// Frontend tests for the React application
// This file contains tests for the main application components

// Test suites:
// - App Component Tests: Tests for the main App component
//   - renders without crashing
//   - shows login page for unauthenticated users
//   - redirects to dashboard for authenticated users
//   - renders navigation for authenticated users

// - Authentication Tests:
//   - redirects to dashboard after successful login
//   - shows error message for invalid credentials
//   - persists authentication across page reloads

// - Chat Interface Tests:
//   - sends messages to the AI agent
//   - displays AI responses correctly
//   - shows loading states during requests
//   - preserves conversation history

// Test utilities:
// - renderWithProviders(): Renders components with all necessary providers
// - mockAuthContext(): Mocks authenticated or unauthenticated states
// - mockApiResponses(): Mocks API responses for predictable testing 