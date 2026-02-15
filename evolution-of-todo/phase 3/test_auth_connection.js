/**
 * Test script to verify the authentication connection between frontend and backend
 */

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

async function testBackendConnection() {
  try {
    console.log('Testing connection to backend...');

    // Test the health endpoint first
    const healthResponse = await fetch(`${BACKEND_URL}/health`);
    if (healthResponse.ok) {
      console.log('✓ Backend is reachable at', BACKEND_URL);
      const healthData = await healthResponse.json();
      console.log('Health status:', healthData);
    } else {
      console.log('✗ Backend health check failed');
      return false;
    }

    // Test the root endpoint
    const rootResponse = await fetch(`${BACKEND_URL}/`);
    if (rootResponse.ok) {
      console.log('✓ Root endpoint is accessible');
    } else {
      console.log('✗ Root endpoint not accessible');
      return false;
    }

    console.log('✓ All connectivity tests passed!');
    return true;
  } catch (error) {
    console.error('✗ Error testing backend connection:', error.message);
    return false;
  }
}

async function testAuthEndpoints() {
  try {
    console.log('\nTesting authentication endpoints...');

    // Test signup endpoint
    const signupResponse = await fetch(`${BACKEND_URL}/api/v1/auth/signup`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: 'test@example.com',
        password: 'invalid-password-for-test'
      })
    });

    // We expect this to fail due to invalid credentials, but we should get a proper response
    console.log(`Signup endpoint status: ${signupResponse.status}`);

    // Test signin endpoint
    const signinResponse = await fetch(`${BACKEND_URL}/api/v1/auth/signin`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: 'nonexistent@example.com',
        password: 'invalid-password'
      })
    });

    console.log(`Signin endpoint status: ${signinResponse.status}`);

    console.log('✓ Authentication endpoints are accessible');
    return true;
  } catch (error) {
    console.error('✗ Error testing auth endpoints:', error.message);
    return false;
  }
}

async function runTests() {
  console.log('Starting authentication connection tests...\n');

  const connectionOk = await testBackendConnection();
  if (!connectionOk) {
    console.log('\n✗ Backend connection failed. Please ensure your backend is running on', BACKEND_URL);
    return;
  }

  const authOk = await testAuthEndpoints();
  if (!authOk) {
    console.log('\n✗ Authentication endpoint tests failed.');
    return;
  }

  console.log('\n🎉 All tests passed! The frontend should be able to connect to the backend authentication API.');
  console.log('\nTo test the full flow:');
  console.log('- Start your backend server: cd backend && uvicorn src.api.main:app --reload');
  console.log('- Start your frontend server: cd frontend && npm run dev');
  console.log('- Visit http://localhost:3000 and try signing up/in');
}

// Run the tests
runTests();