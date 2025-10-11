// OpenWebUI TTS Voice Override
// Paste this into browser console (F12) on the OpenWebUI settings page

// Method 1: Find and set the TTS voice input directly
const ttsVoiceInput = document.querySelector('input[name="ttsVoice"], input[placeholder*="voice" i], select[name="ttsVoice"]');
if (ttsVoiceInput) {
  ttsVoiceInput.value = 'ryan';  // Change to: lessac, amy, joe, alan, alba
  console.log('✅ TTS Voice set to: ryan');
} else {
  console.log('❌ Could not find TTS voice input');
}

// Method 2: If it's a select dropdown, add our voices as options
const selectElement = document.querySelector('select[name="ttsVoice"]');
if (selectElement) {
  const piperVoices = ['lessac', 'amy', 'ryan', 'joe', 'alan', 'alba'];
  piperVoices.forEach(voice => {
    const option = document.createElement('option');
    option.value = voice;
    option.text = voice;
    selectElement.add(option);
  });
  console.log('✅ Added Piper voices to dropdown');
}

// Save the change
console.log('Now click "Save" button to save the setting');
