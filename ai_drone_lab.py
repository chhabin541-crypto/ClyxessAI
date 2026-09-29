def render_ai_autonomous_behavior():
    # ============================================================
    # Imports अंदर हैं ताकि कोई conflict न हो
    # ============================================================
    import streamlit as st
    import streamlit.components.v1 as components

    HTML_TEMPLATE = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Emotional Swarm Drone Game</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
    </head>
    <body class="bg-slate-950 text-slate-100 min-h-screen p-4 font-sans flex flex-col justify-center items-center">

        <div class="w-full max-w-5xl bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-2xl space-y-6">
            
            <!-- Header & Language Selector -->
            <div class="flex flex-col sm:flex-row justify-between items-center pb-4 border-b border-slate-800 gap-4">
                <div class="flex items-center space-x-3">
                    <div class="p-3 bg-purple-500/10 border border-purple-500/30 rounded-2xl text-purple-400">
                        <i class="fa-solid fa-brain-circuit text-2xl"></i>
                    </div>
                    <div>
                        <h1 class="text-xl font-bold text-white tracking-wide">AI Emotional <span class="text-purple-400">Swarm Drone</span></h1>
                        <p class="text-xs text-slate-400">Behavioral Logic & Personality-Driven Drone Simulator</p>
                    </div>
                </div>

                <!-- Multi-Language Support Dropdown -->
                <div class="flex items-center space-x-2 bg-slate-950 px-3 py-2 rounded-xl border border-slate-700">
                    <i class="fa-solid fa-language text-amber-400 text-base"></i>
                    <select id="languageSelect" onchange="changeLanguage()" class="bg-transparent text-amber-400 text-xs font-bold focus:outline-none cursor-pointer">
                        <option value="en" selected>English</option>
                        <option value="hi">हिंदी (Hindi)</option>
                        <option value="te">తెలుగు (Telugu)</option>
                        <option value="ta">தமிழ் (Tamil)</option>
                        <option value="ml">മലയാളം (Malayalam)</option>
                        <option value="kn">ಕನ್ನಡ (Kannada)</option>
                        <option value="bn">বাংলা (Bengali)</option>
                        <option value="gu">ગુજરાતી (Gujarati)</option>
                        <option value="mr">मराठी (Marathi)</option>
                        <option value="or">ଓଡ଼ିଆ (Odia)</option>
                        <option value="pa">ਪੰਜਾਬੀ (Punjabi)</option>
                        <option value="ur">اردو (Urdu)</option>
                        <option value="es">Español</option>
                        <option value="fr">Français</option>
                        <option value="de">Deutsch</option>
                    </select>
                </div>
            </div>

            <!-- Main Game Workspace Grid -->
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">

                <!-- Left Controls: Personality Selection & Logic Blocks -->
                <div class="bg-slate-950 border border-slate-800 rounded-2xl p-5 space-y-4">
                    <h2 class="text-xs font-bold text-slate-300 uppercase tracking-wider border-b border-slate-800 pb-2 flex items-center gap-2">
                        <i class="fa-solid fa-robot text-purple-400"></i> Select AI Drone Agent
                    </h2>

                    <!-- Drone Selection Buttons -->
                    <div class="space-y-2">
                        <button onclick="selectDrone('falcon')" id="btnFalcon" class="w-full p-3 bg-slate-800 border-2 border-purple-500 rounded-xl text-left flex items-center justify-between transition">
                            <div>
                                <p class="text-xs font-bold text-purple-300">🦅 Brave Falcon</p>
                                <p class="text-[10px] text-slate-400 mt-0.5">High speed & aggressive. Needs Energy Shield to pass lasers.</p>
                            </div>
                            <span class="text-[10px] bg-purple-500/20 text-purple-400 px-2 py-0.5 rounded-md font-bold">Brave</span>
                        </button>

                        <button onclick="selectDrone('owl')" id="btnOwl" class="w-full p-3 bg-slate-900 border border-slate-800 rounded-xl text-left flex items-center justify-between transition">
                            <div>
                                <p class="text-xs font-bold text-cyan-300">🦉 Cautious Owl</p>
                                <p class="text-[10px] text-slate-400 mt-0.5">Slow & cautious. Stalls at laser traps without Sonar Scan.</p>
                            </div>
                            <span class="text-[10px] bg-cyan-500/20 text-cyan-400 px-2 py-0.5 rounded-md font-bold">Cautious</span>
                        </button>
                    </div>

                    <!-- Block Toolbox -->
                    <div class="pt-2">
                        <h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Behavioral Logic Blocks</h3>
                        <div class="space-y-2">
                            <button onclick="addBlock('Move Forward')" class="w-full p-2.5 bg-slate-900 border border-slate-700 hover:border-purple-400 rounded-xl text-xs font-bold text-slate-200 text-left flex justify-between items-center transition">
                                <span>🚀 Move Forward</span> <i class="fa-solid fa-plus text-slate-500 text-[10px]"></i>
                            </button>
                            <button onclick="addBlock('Activate Energy Shield')" class="w-full p-2.5 bg-slate-900 border border-slate-700 hover:border-purple-400 rounded-xl text-xs font-bold text-purple-300 text-left flex justify-between items-center transition">
                                <span>🛡️ Activate Energy Shield</span> <i class="fa-solid fa-plus text-slate-500 text-[10px]"></i>
                            </button>
                            <button onclick="addBlock('Sonar Scan Barrier')" class="w-full p-2.5 bg-slate-900 border border-slate-700 hover:border-purple-400 rounded-xl text-xs font-bold text-cyan-300 text-left flex justify-between items-center transition">
                                <span>📡 Sonar Scan Barrier</span> <i class="fa-solid fa-plus text-slate-500 text-[10px]"></i>
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Right Area: Simulation Canvas & Logic Sequence -->
                <div class="lg:col-span-2 bg-slate-950 border border-slate-800 rounded-2xl p-5 flex flex-col justify-between space-y-4">
                    
                    <!-- Arena -->
                    <div class="relative bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col items-center justify-center overflow-hidden h-[220px]">
                        <div class="absolute inset-0 bg-[radial-gradient(#3b82f6_1px,transparent_1px)] [background-size:16px_16px] opacity-20"></div>

                        <!-- Target Point -->
                        <div class="absolute right-8 top-1/2 -translate-y-1/2 w-12 h-12 bg-emerald-500/10 border-2 border-emerald-400 rounded-full flex items-center justify-center animate-pulse">
                            <i class="fa-solid fa-bullseye text-emerald-400 text-xl"></i>
                        </div>

                        <!-- Laser Hazard -->
                        <div id="laserBarrier" class="absolute left-1/2 top-0 bottom-0 w-2 bg-rose-500 shadow-[0_0_15px_#f43f5e] z-10 flex items-center justify-center">
                            <span class="text-[9px] bg-rose-950 text-rose-300 font-bold px-1 rounded -rotate-90">LASER TRAP</span>
                        </div>

                        <!-- Drone Unit -->
                        <div id="droneSprite" class="absolute left-8 top-1/2 -translate-y-1/2 transition-all duration-700 z-20 flex flex-col items-center">
                            <i id="droneIcon" class="fa-solid fa-helicopter text-4xl text-purple-400"></i>
                            <span id="droneAITag" class="text-[9px] font-bold bg-slate-950 px-2 py-0.5 rounded-full border border-purple-500/40 text-purple-300 mt-1">Brave AI</span>
                        </div>
                    </div>

                    <!-- Chain Sequence Area -->
                    <div class="bg-slate-900 border border-slate-800 rounded-xl p-4">
                        <div class="flex justify-between items-center mb-2">
                            <h4 class="text-xs font-bold text-slate-400 uppercase tracking-wider">AI Execution Sequence</h4>
                            <button onclick="clearSequence()" class="text-[10px] text-rose-400 hover:underline">Clear Sequence</button>
                        </div>
                        <div id="sequenceList" class="min-h-[60px] border border-dashed border-slate-800 rounded-xl p-2 flex flex-wrap gap-2 items-center">
                            <p class="text-xs text-slate-600 italic">Click blocks to chain logic sequence...</p>
                        </div>
                    </div>

                    <!-- Action Bar -->
                    <div class="flex flex-col sm:flex-row justify-between items-center pt-2 border-t border-slate-800 gap-3">
                        <p id="statusFeedback" class="text-xs font-bold text-slate-400">Status: Ready for deployment</p>
                        <button onclick="runAISwarm()" class="w-full sm:w-auto px-6 py-2.5 bg-purple-500 hover:bg-purple-400 text-slate-950 text-xs font-bold rounded-xl shadow-lg shadow-purple-500/20 transition flex items-center justify-center gap-2">
                            <i class="fa-solid fa-bolt"></i> Execute AI Swarm Logic
                        </button>
                    </div>

                </div>

            </div>
        </div>

        <script>
            let currentDrone = "falcon";
            let sequence = [];
            let currentLang = "en";

            const translations = {
                "en": {
                    successFalcon: "🎉 Success! Brave Falcon used Shield to cross Laser Barrier!",
                    crashFalcon: "💥 Crash! Brave Falcon was too aggressive and hit Laser without Shield!",
                    successOwl: "🎉 Success! Cautious Owl scanned the barrier & crossed safely!",
                    stallOwl: "⚠️ Stalled! Cautious Owl detected Laser Hazard & refused to move without Sonar Scan!",
                    emptyError: "❌ Please add at least 1 logic block!"
                },
                "hi": {
                    successFalcon: "🎉 सफलता! Brave Falcon ने Laser Barrier पार करने के लिए Shield का उपयोग किया!",
                    crashFalcon: "💥 क्रैश! Brave Falcon बहुत तेज था और बिना Shield के Laser से टकरा गया!",
                    successOwl: "🎉 सफलता! Cautious Owl ने बैरियर को स्कैन किया और सुरक्षित पार किया!",
                    stallOwl: "⚠️ रुकावट! Cautious Owl ने लेजर देखा और बिना Sonar Scan के आगे बढ़ने से मना कर दिया!",
                    emptyError: "❌ कृपया कम से कम 1 लॉजिक ब्लॉक जोड़ें!"
                },
                "te": {
                    successFalcon: "🎉 విజయం! Brave Falcon లేజర్ బారియర్‌ను దాటడానికి షీల్డ్‌ని ఉపయోగించింది!",
                    crashFalcon: "💥 క్రాష్! Brave Falcon షీల్డ్ లేకుండా లేజర్‌ను ఢీకొట్టింది!",
                    successOwl: "🎉 విజయం! Cautious Owl బారియర్‌ను స్కాన్ చేసి సురక్షితంగా దాటింది!",
                    stallOwl: "⚠️ నిలిచిపోయింది! Cautious Owl సోనార్ స్కాన్ లేకుండా ముందుకు సాగలేదు!",
                    emptyError: "❌ దయచేసి కనీసం 1 లాజిక్ బ్లాక్‌ను జోడించండి!"
                },
                "ta": {
                    successFalcon: "🎉 வெற்றி! Brave Falcon லேசர் தடையைக் கடக்க கேடயத்தைப் பயன்படுத்தியது!",
                    crashFalcon: "💥 விபத்து! Brave Falcon கேடயம் இல்லாமல் லேசரில் மோதியது!",
                    successOwl: "🎉 வெற்றி! Cautious Owl தடையை ஸ்கேன் செய்து பாதுகாப்பாகக் கடந்தது!",
                    stallOwl: "⚠️ நின்றது! Cautious Owl சோனார் ஸ்கேன் இல்லாமல் நகர மறுத்துவிட்டது!",
                    emptyError: "❌ தயவுசெய்து குறைந்தபட்சம் 1 லாஜிக் பிளாக்கைச் சேர்க்கவும்!"
                },
                "mr": {
                    successFalcon: "🎉 यश! Brave Falcon ने लेझर बॅरियर पार करण्यासाठी शील्ड वापरली!",
                    crashFalcon: "💥 क्रॅश! Brave Falcon शील्डशिवाय लेझरला धडकला!",
                    successOwl: "🎉 यश! Cautious Owl ने बॅरियर स्कॅन केले आणि सुरक्षितपणे पार केले!",
                    stallOwl: "⚠️ थांबला! Cautious Owl ने सोन्यार स्कॅनशिवाय पुढे जाण्यास नकार दिला!",
                    emptyError: "❌ कृपया किमान १ लॉजिक ब्लॉक जोडा!"
                },
                "gu": {
                    successFalcon: "🎉 સફળતા! Brave Falcon એ લેઝર બેરિયર પાર કરવા માટે શીલ્ડનો ઉપયોગ કર્યો!",
                    crashFalcon: "💥 ક્રેશ! Brave Falcon શીલ્ડ વગર લેઝર સાથે અથડાયું!",
                    successOwl: "🎉 સફળતા! Cautious Owl એ બેરિયર સ્કેન કર્યું અને સુરક્ષિત રીતે પાર કર્યું!",
                    stallOwl: "⚠️ અટકી ગયું! Cautious Owl એ સોનાર સ્કેન વગર આગળ વધવાની ના પાડી!",
                    emptyError: "❌ કૃપા કરીને ઓછામાં ઓછું ૧ લોજિક બ્લોક ઉમેરો!"
                },
                "bn": {
                    successFalcon: "🎉 সাফল্য! Brave Falcon লেজার ব্যারিয়ার পার হতে শিল্ড ব্যবহার করেছে!",
                    crashFalcon: "💥 ক্র্যাশ! Brave Falcon শিল্ড ছাড়া লেজারে ধাক্কা খেয়েছে!",
                    successOwl: "🎉 সাফল্য! Cautious Owl ব্যারিয়ার স্ক্যান করে নিরাপদে পার হয়েছে!",
                    stallOwl: "⚠️ থমকে গেছে! Cautious Owl সোনার স্ক্যান ছাড়া এগোতে রাজি হয়নি!",
                    emptyError: "❌ অনুগ্রহ করে অন্তত ১টি লজিক ব্লক যোগ করুন!"
                }
            };

            function changeLanguage() {
                currentLang = document.getElementById('languageSelect').value;
            }

            function selectDrone(type) {
                currentDrone = type;
                const btnF = document.getElementById('btnFalcon');
                const btnO = document.getElementById('btnOwl');
                const icon = document.getElementById('droneIcon');
                const tag = document.getElementById('droneAITag');

                if(type === 'falcon') {
                    btnF.className = "w-full p-3 bg-slate-800 border-2 border-purple-500 rounded-xl text-left flex items-center justify-between transition";
                    btnO.className = "w-full p-3 bg-slate-900 border border-slate-800 rounded-xl text-left flex items-center justify-between transition";
                    icon.className = "fa-solid fa-helicopter text-4xl text-purple-400";
                    tag.innerText = "Brave AI";
                    tag.className = "text-[9px] font-bold bg-slate-950 px-2 py-0.5 rounded-full border border-purple-500/40 text-purple-300 mt-1";
                } else {
                    btnO.className = "w-full p-3 bg-slate-800 border-2 border-cyan-500 rounded-xl text-left flex items-center justify-between transition";
                    btnF.className = "w-full p-3 bg-slate-900 border border-slate-800 rounded-xl text-left flex items-center justify-between transition";
                    icon.className = "fa-solid fa-paper-plane text-4xl text-cyan-400";
                    tag.innerText = "Cautious AI";
                    tag.className = "text-[9px] font-bold bg-slate-950 px-2 py-0.5 rounded-full border border-cyan-500/40 text-cyan-300 mt-1";
                }
                resetDronePos();
            }

            function addBlock(text) {
                sequence.push(text);
                renderSequence();
            }

            function renderSequence() {
                const list = document.getElementById('sequenceList');
                list.innerHTML = '';
                if(sequence.length === 0) {
                    list.innerHTML = '<p class="text-xs text-slate-600 italic">Click blocks to chain logic sequence...</p>';
                    return;
                }

                sequence.forEach((item, index) => {
                    const b = document.createElement('span');
                    b.className = "bg-purple-500/20 text-purple-300 border border-purple-500/40 text-xs px-2.5 py-1 rounded-lg font-bold flex items-center gap-1.5";
                    b.innerHTML = `${index + 1}. ${item} <i onclick="removeBlock(${index})" class="fa-solid fa-xmark text-[10px] ml-1 cursor-pointer hover:text-rose-400"></i>`;
                    list.appendChild(b);
                });
            }

            function removeBlock(index) {
                sequence.splice(index, 1);
                renderSequence();
            }

            function clearSequence() {
                sequence = [];
                renderSequence();
                resetDronePos();
            }

            function resetDronePos() {
                document.getElementById('droneSprite').style.left = '32px';
                document.getElementById('statusFeedback').className = "text-xs font-bold text-slate-400";
                document.getElementById('statusFeedback').innerText = "Status: Ready for deployment";
            }

            function runAISwarm() {
                const sprite = document.getElementById('droneSprite');
                const feedback = document.getElementById('statusFeedback');

                const t = translations[currentLang] || translations["en"];

                if(sequence.length === 0) {
                    feedback.innerText = t.emptyError;
                    feedback.className = "text-xs font-bold text-rose-400";
                    return;
                }

                const hasShield = sequence.includes("Activate Energy Shield");
                const hasSonar = sequence.includes("Sonar Scan Barrier");

                if(currentDrone === 'falcon') {
                    if(hasShield) {
                        sprite.style.left = '80%';
                        feedback.innerText = t.successFalcon;
                        feedback.className = "text-xs font-bold text-emerald-400";
                        confetti({ particleCount: 110, spread: 75, origin: { y: 0.6 } });
                    } else {
                        sprite.style.left = '45%';
                        feedback.innerText = t.crashFalcon;
                        feedback.className = "text-xs font-bold text-rose-400";
                    }
                } else if(currentDrone === 'owl') {
                    if(hasSonar) {
                        sprite.style.left = '80%';
                        feedback.innerText = t.successOwl;
                        feedback.className = "text-xs font-bold text-emerald-400";
                        confetti({ particleCount: 110, spread: 75, origin: { y: 0.6 } });
                    } else {
                        sprite.style.left = '35%';
                        feedback.innerText = t.stallOwl;
                        feedback.className = "text-xs font-bold text-amber-400";
                    }
                }
            }
        </script>
    </body>
    </html>
    """
    
    # यह लाइन HTML को Streamlit में दिखाएगी
    components.html(HTML_TEMPLATE, height=850, scrolling=True)
