// MA Marketing – originalna muzika za reels „mapa“ (13.5 s, 120 BPM, f-mol / As-dur)
// Rezovi u videu: 2.5 (drugi natpis), 5.0 (crveni ekran), 7.0 (rješenje), 10.0 (kraj), 13.5 (kraj videa)
// Takt = 0.5 s. Sve je fiksno (bez slučajnosti po renderu).
const NB = 'https://cdn.jsdelivr.net/gh/nbrosowsky/tonejs-instruments@master/samples/';
const GM = 'https://cdn.jsdelivr.net/gh/gleitz/midi-js-soundfonts@gh-pages/FluidR3_GM/';

function rng(seed) { return () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }

async function buildScore(log) {
  const R = rng(7);
  const B = 0.5;           // jedan takt (beat)
  const T = b => b * B;    // takt -> sekunde

  // --- busevi ---
  const master = new Tone.Compressor({ threshold: -14, ratio: 3, attack: 0.01, release: 0.2 }).toDestination();
  const rev = new Tone.Reverb({ decay: 2.6, wet: 1 }); await rev.generate();
  const revIn = new Tone.Filter(300, 'highpass').connect(rev); rev.connect(new Tone.Gain(0.35).connect(master));
  const bus = (db, send = 0) => { const g = new Tone.Gain(Tone.dbToGain(db)).connect(master); if (send) { const s = new Tone.Gain(send); g.connect(s); s.connect(revIn); } return g; };

  // --- instrumenti (pravi snimci) ---
  const pianoNotes = ['A1','A2','A3','A4','A5','C2','C3','C4','C5','C6','Ds2','Ds3','Ds4','Ds5','Fs2','Fs3','Fs4','Fs5'];
  const piano = new Tone.Sampler({ urls: Object.fromEntries(pianoNotes.map(n => [n.replace('s', '#'), n + '.mp3'])), baseUrl: NB + 'piano/', release: 1.2 });
  const pianoOut = bus(-6, 0.45); piano.connect(pianoOut);
  const mNotes = ['C4','Eb4','Gb4','A4','C5','Eb5','Gb5','A5','C6'];
  const marimba = new Tone.Sampler({ urls: Object.fromEntries(mNotes.map(n => [n, n + '.mp3'])), baseUrl: GM + 'marimba-mp3/', release: 0.6 });
  const marOut = bus(-9, 0.3); marimba.connect(new Tone.Panner(0.25).connect(marOut));
  const cNotes = ['A2','C3','E3','G3','A3','C4','E4','G4'];
  const cello = new Tone.Sampler({ urls: Object.fromEntries(cNotes.map(n => [n, n + '.mp3'])), baseUrl: NB + 'cello/', attack: 0.25, release: 1.5 });
  const celloOut = bus(-13, 0.6); cello.connect(celloOut);

  // --- ritam (sintetizovan, kao u modernoj produkciji) ---
  const kick = new Tone.MembraneSynth({ pitchDecay: 0.05, octaves: 6, envelope: { attack: 0.001, decay: 0.4, sustain: 0, release: 0.1 } }).connect(bus(-4));
  const hatF = new Tone.Filter(8000, 'highpass').connect(new Tone.Panner(-0.2).connect(bus(-20, 0.1)));
  const hat = new Tone.NoiseSynth({ noise: { type: 'white' }, envelope: { attack: 0.001, decay: 0.05, sustain: 0 } }).connect(hatF);
  const clapF = new Tone.Filter({ frequency: 1500, type: 'bandpass', Q: 0.8 }).connect(bus(-11, 0.35));
  const clap = new Tone.NoiseSynth({ noise: { type: 'pink' }, envelope: { attack: 0.002, decay: 0.16, sustain: 0 } }).connect(clapF);
  const bass = new Tone.MonoSynth({ oscillator: { type: 'sawtooth' }, filter: { Q: 1, type: 'lowpass' }, filterEnvelope: { attack: 0.005, decay: 0.15, sustain: 0.3, baseFrequency: 90, octaves: 2.2 }, envelope: { attack: 0.005, decay: 0.2, sustain: 0.7, release: 0.12 } }).connect(bus(-12));
  const sub = new Tone.Synth({ oscillator: { type: 'sine' }, envelope: { attack: 0.01, decay: 0.3, sustain: 0.8, release: 0.3 } }).connect(bus(-14));
  const riseF = new Tone.AutoFilter({ frequency: 0, baseFrequency: 400, octaves: 0 }).start();
  const riserF = new Tone.Filter(400, 'bandpass'); const riser = new Tone.NoiseSynth({ noise: { type: 'pink' }, envelope: { attack: 1.8, decay: 0.01, sustain: 1, release: 0.05 } }).connect(riserF);
  riserF.connect(bus(-16, 0.5));

  await Tone.loaded();
  log && log(1, 1);

  const hum = (t, amt = 0.012) => Math.max(0, t + (R() - 0.5) * amt);   // ljudski pomak
  const HATS = []; const hatAt = (d, t, v) => HATS.push([t, d, v]);
  const vel = (v, amt = 0.12) => Math.max(0.05, Math.min(1, v + (R() - 0.5) * amt));

  // akordi (f-mol): Fm – Db – Ab – Eb ; po 2 takta svaki u A, po 4 u C/D
  const CH = { Fm: ['F3','Ab3','C4'], Db: ['Db3','F3','Ab3'], Ab: ['Ab3','C4','Eb4'], Eb: ['Eb3','G3','Bb3'] };
  const BASS = { Fm: 'F1', Db: 'Db1', Ab: 'Ab1', Eb: 'Eb1' };

  // ===== A: 0–5 s (takt 0–10) mapa: arpeggio klavira + puls, napetost raste =====
  const arpA = [['F4','Ab4','C5','Ab4'], ['F4','Ab4','C5','Ab4'], ['Db4','F4','Ab4','F4'], ['Db4','F4','Ab4','F4'], ['Eb4','G4','Bb4','G4']];
  for (let bar = 0; bar < 5; bar++) {           // 5 × 2 takta = 10 taktova
    for (let i = 0; i < 4; i++) {
      const b = bar * 2 + i * 0.5;
      piano.triggerAttackRelease(arpA[bar][i], 0.4, hum(T(b)), vel(0.42 + bar * 0.06 + (i === 0 ? 0.1 : 0)));
    }
  }
  piano.triggerAttackRelease(['F2', 'C3'], 2.4, 0, 0.55);
  piano.triggerAttackRelease(['Db2', 'Ab2'], 2.4, T(4), 0.5);
  piano.triggerAttackRelease(['Eb2', 'Bb2'], 1.0, T(8), 0.55);
  cello.triggerAttackRelease('C3', 4.6, 0.02, 0.5);
  for (let b = 0; b < 10; b++) sub.triggerAttackRelease(b < 4 ? 'F1' : b < 8 ? 'Db1' : 'Eb1', 0.2, T(b), 0.35 + b * 0.03);
  for (let b = 4; b < 10; b += 0.5) hatAt(0.03, hum(T(b), 0.006), vel(b % 1 ? 0.25 : 0.4));
  marimba.triggerAttackRelease('C5', 0.3, T(5), 0.6);          // drugi natpis na 2.5 s
  marimba.triggerAttackRelease('Eb5', 0.3, T(5.5), 0.45);
  riser.triggerAttackRelease(1.85, T(6.3), 0.5);                // dizanje u crveni ekran

  // ===== B: 5–7 s (takt 10–14) crveni ekran: udar pa tišina =====
  kick.triggerAttackRelease('C1', 0.5, T(10), 1);
  piano.triggerAttackRelease(['F1', 'F2', 'C3', 'Ab3'], 1.9, T(10), 0.85);
  bass.triggerAttackRelease('F1', 0.9, T(10), 0.8);
  cello.triggerAttackRelease('F3', 1.8, T(10.1), 0.45);
  piano.triggerAttackRelease('C5', 0.5, T(12), 0.3);
  piano.triggerAttackRelease('Ab4', 0.5, T(12.5), 0.28);
  riser.triggerAttackRelease(1.0, T(12), 0.6);
  for (let b = 13; b < 14; b += 0.25) hatAt(0.02, T(b), 0.2 + (b - 13) * 0.4);

  // ===== C: 7–10 s (takt 14–20) rješenje: puni groove u As-duru =====
  // ===== D: 10–13.5 s (takt 20–27) kraj: groove lakši, završni akord =====
  const prog = ['Ab', 'Ab', 'Db', 'Db', 'Eb', 'Eb', 'Fm', 'Fm', 'Db', 'Db', 'Eb', 'Eb', 'Ab'];
  for (let b = 14; b < 27; b++) {
    const ch = prog[Math.min(prog.length - 1, Math.floor((b - 14) / 1))];
    const end = b >= 26;
    kick.triggerAttackRelease('C1', 0.4, T(b), b === 14 || b === 20 ? 1 : 0.8);
    if (b % 2 === 1 && !end) clap.triggerAttackRelease(0.12, hum(T(b), 0.008), vel(0.7));
    if (!end) { hatAt(0.03, hum(T(b + 0.5), 0.006), vel(b >= 20 ? 0.3 : 0.45)); }
    if (b < 20 && !end) hatAt(0.02, hum(T(b + 0.25)), 0.18), hatAt(0.02, hum(T(b + 0.75)), 0.18);
    bass.triggerAttackRelease(BASS[ch], 0.22, T(b), 0.75);
    if (!end) bass.triggerAttackRelease(BASS[ch].replace('1', '2'), 0.15, T(b + 0.5), 0.5);
    if (b % 2 === 0) piano.triggerAttackRelease(CH[ch], end ? 2.5 : 0.9, hum(T(b) + 0.01), vel(0.5));
  }
  // melodija marimbe (pozitivna, ide gore) – kreće s rješenjem
  const mel = [['Eb5', 14], ['C5', 14.5], ['Eb5', 15], ['F5', 15.5], ['Ab5', 16], ['F5', 16.75], ['Eb5', 17.5], ['C5', 18], ['Eb5', 18.5], ['Bb4', 19.25],
               ['C5', 20], ['Eb5', 20.5], ['F5', 21], ['Eb5', 22], ['C5', 22.5], ['Bb4', 23], ['C5', 24], ['Eb5', 24.5], ['Ab5', 26]];
  mel.forEach(([n, b], i) => marimba.triggerAttackRelease(n, 0.35, hum(T(b) + 0.025), vel(0.55 + 0.25 * Math.sin(i / mel.length * Math.PI))));
  cello.triggerAttackRelease('Ab2', 3.2, T(14), 0.4);
  cello.triggerAttackRelease('C3', 3.0, T(20), 0.35);
  piano.triggerAttackRelease(['Ab1', 'Ab2', 'Eb3', 'C4', 'Eb4', 'Ab4'], 3.0, T(26), 0.6);
  HATS.sort((a, b) => a[0] - b[0]); let last = -1;
  for (const [t, d, v] of HATS) { const tt = Math.max(t, last + 0.01); hat.triggerAttackRelease(d, tt, v); last = tt; }
}
