# ModularSampler
A Raspberry Pi-based sampler designed to integrate with a modular synthesizer



Connections needed
* Audio input
* Audio output
* MIDI input (can be USB)
* MIDI output for sampling a MIDI synth (optional)
* CV, trig, gate output
* Some buttons and LEDs (optional)

Hardware needed
* RPi
* Audio Injector
* Audio level adapter (could be a separate module)
* Another board
  * Filter PWM from GPIO for CV
  * Buffer trig and gate from GPIO
  * Buttons and LEDs

MIDI CV mode
* MIDI notes produce CV/trig/gate output
* No recording or playback of audio

Record mode
* MIDI notes produce CV/trig/gate output
* MIDI note also starts audio recording
* Audio recording continues after MIDI note is released up to a certain time

Playback mode
* MIDI notes play back the previous audio recording
* No CV/trig/gate output

Autosample mode
* Define a note range, note length, and release length
* Produces CV/trig/gate output for each note in the range and records audio


### TODO list

MIDI
* ✓ Get MIDI messages from USB

Audio out
* ✓ Get audio output through card
* ✓ Play audio from Python
* ✓ Load a sample
* Build an amplifier to get to eurorack levels

Audio in
* ✓ Get audio input through card
* ✓ Record audio from Python
* ✓ Save a sample
* Build an attenuator to get from eurorack levels

CV
* ✓ Generate digital output
* Generate PWM output
* Build a trigger out buffer
* Build a CV out buffer/filter

Integration
* ✓ MIDI to CV mode
* ✓ Record mode
* ✓ Playback mode
* Autosample mode
* Interactive application


### Wishlist

* MIDI DIN input
* Custom hat PCB
* Build it into a eurorack module
* Port to RPi Zero
* All-button interface
* Velocity sampling
