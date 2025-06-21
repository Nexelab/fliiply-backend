/**
 * Bruno Environment Setup Script
 * 
 * This script helps configure environment variables for different deployment environments.
 * Run this after importing the Bruno collection to set up your testing environment.
 */

// Environment configurations
const environments = {
  development: {
    baseUrl: 'http://localhost:8000',
    apiPath: '/api',
    description: 'Local development server'
  },
  staging: {
    baseUrl: 'https://staging-api.fliply.com',
    apiPath: '/api',
    description: 'Staging environment for testing'
  },
  production: {
    baseUrl: 'https://api.fliply.com',
    apiPath: '/api',
    description: 'Production environment - use with caution'
  }
};

// Test user credentials for different environments
const testCredentials = {
  development: {
    buyer: {
      email: 'buyer@test.com',
      password: 'TestPassword123!'
    },
    seller: {
      email: 'seller@test.com',
      password: 'TestPassword123!'
    },
    admin: {
      email: 'admin@test.com',
      password: 'AdminPassword123!'
    }
  },
  staging: {
    buyer: {
      email: 'staging-buyer@fliply.com',
      password: 'StagingPassword123!'
    },
    seller: {
      email: 'staging-seller@fliply.com',
      password: 'StagingPassword123!'
    },
    admin: {
      email: 'staging-admin@fliply.com',
      password: 'AdminStagingPassword123!'
    }
  }
  // Production credentials should not be hardcoded
};

// Sample test data
const sampleData = {
  addresses: {
    shipping: {
      address_type: 'shipping',
      street: '123 Main Street',
      city: 'Paris',
      state: 'Île-de-France',
      postal_code: '75001',
      country: 'France',
      is_default: true
    },
    billing: {
      address_type: 'billing',
      street: '456 Business Ave',
      city: 'Lyon',
      state: 'Auvergne-Rhône-Alpes',
      postal_code: '69001',
      country: 'France',
      is_default: false
    }
  },
  products: {
    charizard: {
      name: 'Charizard',
      series: 'Base Set',
      rarity: 'Rare Holo',
      hp: '120',
      attack: '100',
      defense: '78'
    },
    pikachu: {
      name: 'Pikachu',
      series: 'Base Set',
      rarity: 'Common',
      hp: '60',
      attack: '55',
      defense: '40'
    }
  },
  listings: {
    charizard_nm: {
      condition: 'Near Mint',
      price: '299.99',
      quantity: 1,
      description: 'Perfect condition Charizard from Base Set. Never played, stored in protective sleeve.'
    },
    pikachu_played: {
      condition: 'Played',
      price: '45.00',
      quantity: 3,
      description: 'Played condition Pikachu. Some edge wear but still displayable.'
    }
  }
};

/**
 * Setup instructions for each environment
 */
function getSetupInstructions(env) {
  const config = environments[env];
  const creds = testCredentials[env];
  
  console.log(`\n=== ${env.toUpperCase()} ENVIRONMENT SETUP ===`);
  console.log(`Description: ${config.description}`);
  console.log(`Base URL: ${config.baseUrl}`);
  console.log(`API Path: ${config.apiPath}`);
  
  if (creds) {
    console.log('\n--- Test Credentials ---');
    console.log(`Buyer: ${creds.buyer.email} / ${creds.buyer.password}`);
    console.log(`Seller: ${creds.seller.email} / ${creds.seller.password}`);
    console.log(`Admin: ${creds.admin.email} / ${creds.admin.password}`);
  }
  
  console.log('\n--- Setup Steps ---');
  console.log('1. Open Bruno and import the bruno-collection folder');
  console.log(`2. Select "${env}" environment from the dropdown`);
  console.log('3. Verify environment variables are set correctly');
  console.log('4. Run Authentication > Login to get access token');
  console.log('5. Start testing endpoints!');
  
  if (env === 'production') {
    console.log('\n⚠️  WARNING: You are setting up PRODUCTION environment!');
    console.log('   - Use real credentials (not test accounts)');
    console.log('   - Be careful with data modifications');
    console.log('   - Consider using staging for testing first');
  }
}

/**
 * Generate Bruno environment file content
 */
function generateBrunoEnvFile(env) {
  const config = environments[env];
  
  return `vars {
  baseUrl: ${config.baseUrl}
  apiPath: ${config.apiPath}
  accessToken: 
  refreshToken: 
}

vars:secret [
  
]`;
}

/**
 * Main setup function
 */
function setupEnvironment() {
  console.log('🚀 Bruno API Collection Setup\n');
  console.log('Available environments:');
  
  Object.keys(environments).forEach((env, index) => {
    console.log(`${index + 1}. ${env} - ${environments[env].description}`);
  });
  
  console.log('\nTo setup a specific environment, run:');
  console.log('getSetupInstructions("development")');
  console.log('getSetupInstructions("staging")');
  console.log('getSetupInstructions("production")');
  
  console.log('\nTo generate Bruno environment file:');
  console.log('generateBrunoEnvFile("development")');
}

// Export functions for use
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    environments,
    testCredentials,
    sampleData,
    getSetupInstructions,
    generateBrunoEnvFile,
    setupEnvironment
  };
}

// Auto-run setup if script is executed directly
if (typeof window === 'undefined' && require.main === module) {
  setupEnvironment();
}