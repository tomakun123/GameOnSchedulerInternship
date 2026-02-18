/**
 * Basic Vapi Node.js SDK Example
 * 
 * This example demonstrates how to use the Vapi Node.js SDK to manage assistants
 * and make phone calls programmatically.
 */

require('dotenv').config();
const Vapi = require('@vapi-ai/server-sdk').Vapi;

// Initialize Vapi client
const client = new Vapi({
  apiKey: process.env.VAPI_API_KEY,
});

async function listAssistants() {
  try {
    const assistants = await client.assistants.list();
    console.log(`Found ${assistants.length} assistants:`);
    assistants.forEach(assistant => {
      console.log(`  - ${assistant.name} (ID: ${assistant.id})`);
    });
    return assistants;
  } catch (error) {
    console.error('Error listing assistants:', error);
    return [];
  }
}

async function createAssistant() {
  try {
    const assistant = await client.assistants.create({
      name: 'Node.js SDK Assistant',
      model: {
        provider: 'openai',
        model: 'gpt-4',
        messages: [
          {
            role: 'system',
            content: 'You are a helpful assistant created via the Node.js SDK.'
          }
        ]
      },
      voice: {
        provider: 'elevenlabs',
        voiceId: '21m00Tcm4TlvDq8ikWAM' // Rachel voice
      }
    });
    console.log(`Created assistant: ${assistant.name} (ID: ${assistant.id})`);
    return assistant;
  } catch (error) {
    console.error('Error creating assistant:', error);
    return null;
  }
}

async function makePhoneCall(assistantId, phoneNumber) {
  try {
    const call = await client.calls.create({
      assistantId,
      customer: {
        number: phoneNumber
      }
    });
    console.log(`Call initiated! Call ID: ${call.id}`);
    console.log(`Status: ${call.status}`);
    return call;
  } catch (error) {
    console.error('Error making call:', error);
    return null;
  }
}

async function main() {
  console.log('🚀 Vapi Node.js SDK Example');
  console.log('-'.repeat(50));
  
  // List existing assistants
  console.log('\n📋 Listing assistants...');
  const assistants = await listAssistants();
  
  // Create a new assistant
  console.log('\n✨ Creating a new assistant...');
  const newAssistant = await createAssistant();
  
  if (newAssistant) {
    // Example of making a call (commented out for safety)
    // console.log('\n📞 Making a phone call...');
    // await makePhoneCall(newAssistant.id, '+1234567890');
    console.log('\n💡 To make a phone call, uncomment the code above and provide a valid phone number');
  }
  
  console.log('\n✅ Example completed!');
}

// Run the example
main().catch(console.error);
