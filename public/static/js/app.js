document.addEventListener("DOMContentLoaded", () => {
    lucide.createIcons();

    // DOM Elements
    const themeToggle = document.getElementById("themeToggle");
    const themeIcon = document.getElementById("themeIcon");
    const modelSelect = document.getElementById("modelSelect");
    const modelSelectWrapper = document.getElementById("modelSelectWrapper");
    const platBtns = document.querySelectorAll(".plat-btn");

    const geminiEnvBadge = document.getElementById("geminiEnvBadge");
    const openKeysModalBtn = document.getElementById("openKeysModalBtn");
    const keysModal = document.getElementById("keysModal");
    const closeKeysModalBtn = document.getElementById("closeKeysModalBtn");
    const geminiKeysInput = document.getElementById("geminiKeysInput");
    const keyStatusSummary = document.getElementById("keyStatusSummary");
    const reloadEnvBtn = document.getElementById("reloadEnvBtn");
    const saveKeysBtn = document.getElementById("saveKeysBtn");

    const dropZone = document.getElementById("dropZone");
    const fileInput = document.getElementById("fileInput");
    const fileStatus = document.getElementById("fileStatus");
    const fileName = document.getElementById("fileName");
    const fileType = document.getElementById("fileType");
    const clearFileBtn = document.getElementById("clearFileBtn");

    const problemInput = document.getElementById("problemInput");
    const charCount = document.getElementById("charCount");
    const pasteBtn = document.getElementById("pasteBtn");
    const clearTextBtn = document.getElementById("clearTextBtn");

    const solveBtn = document.getElementById("solveBtn");
    const solveBtnText = document.getElementById("solveBtnText");
    const stopBtn = document.getElementById("stopBtn");

    const singleViewContainer = document.getElementById("singleViewContainer");
    const dualViewContainer = document.getElementById("dualViewContainer");

    const emptyState = document.getElementById("emptyState");
    const streamStatus = document.getElementById("streamStatus");
    const streamStatusText = document.getElementById("streamStatusText");
    const markdownOutput = document.getElementById("markdownOutput");

    const streamStatusLeft = document.getElementById("streamStatusLeft");
    const markdownOutputLeft = document.getElementById("markdownOutputLeft");
    const streamStatusRight = document.getElementById("streamStatusRight");
    const markdownOutputRight = document.getElementById("markdownOutputRight");

    const copyDualLeftBtn = document.getElementById("copyDualLeftBtn");
    const copyDualRightBtn = document.getElementById("copyDualRightBtn");

    const tabBtns = document.querySelectorAll(".tab-btn");
    const tabPanes = document.querySelectorAll(".tab-pane");

    const subtasksContent = document.getElementById("subtasksContent");
    const cppCode = document.getElementById("cppCode");
    const pyCode = document.getElementById("pyCode");
    const genScriptCode = document.getElementById("genScriptCode");
    const testsAnalysis = document.getElementById("testsAnalysis");

    const copyAllBtn = document.getElementById("copyAllBtn");
    const copyCppBtn = document.getElementById("copyCppBtn");
    const downloadCppBtn = document.getElementById("downloadCppBtn");
    const copyPyBtn = document.getElementById("copyPyBtn");
    const downloadPyBtn = document.getElementById("downloadPyBtn");
    const copyGenBtn = document.getElementById("copyGenBtn");
    const downloadGenBtn = document.getElementById("downloadGenBtn");

    const toast = document.getElementById("toast");
    const toastMessage = document.getElementById("toastMessage");

    let currentProvider = "ollama"; // "ollama", "gemini", or "parallel"
    let currentAbortController = null;
    let currentAbortController2 = null;
    let fullMarkdownText = "";
    let fullMarkdownTextLeft = "";
    let fullMarkdownTextRight = "";
    let sampleProblemsData = [];
    let ollamaModelsList = [];

    // ===== THEME MANAGEMENT =====
    const savedTheme = localStorage.getItem("hsg_theme") || "dark";
    if (savedTheme === "light") {
        document.body.classList.remove("dark-theme");
        document.body.classList.add("light-theme");
        themeIcon.setAttribute("data-lucide", "moon");
    } else {
        document.body.classList.remove("light-theme");
        document.body.classList.add("dark-theme");
        themeIcon.setAttribute("data-lucide", "sun");
    }
    lucide.createIcons();

    themeToggle.addEventListener("click", () => {
        const isLight = document.body.classList.contains("light-theme");
        if (isLight) {
            document.body.classList.remove("light-theme");
            document.body.classList.add("dark-theme");
            localStorage.setItem("hsg_theme", "dark");
            themeIcon.setAttribute("data-lucide", "sun");
        } else {
            document.body.classList.remove("dark-theme");
            document.body.classList.add("light-theme");
            localStorage.setItem("hsg_theme", "light");
            themeIcon.setAttribute("data-lucide", "moon");
        }
        lucide.createIcons();
    });

    function showToast(message, type = "success") {
        toastMessage.textContent = message;
        toast.className = "toast";
        if (type === "error") {
            toast.style.backgroundColor = "var(--accent-red)";
        } else {
            toast.style.backgroundColor = "#2ea043";
        }
        toast.classList.remove("hidden");
        setTimeout(() => {
            toast.classList.add("hidden");
        }, 3000);
    }

    // ===== PLATFORM SELECTOR (Ollama / Gemini / Parallel) =====
    platBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            platBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            currentProvider = btn.getAttribute("data-provider");
            updatePlatformUI();
        });
    });

    function updatePlatformUI() {
        if (currentProvider === "ollama") {
            solveBtnText.textContent = "GIẢI ĐỀ BẰNG OLLAMA LOCAL";
            solveBtn.style.background = "linear-gradient(135deg, var(--accent-blue), #1f6feb)";
            modelSelectWrapper.classList.remove("hidden");
            populateModelSelect("ollama");
            singleViewContainer.classList.remove("hidden");
            dualViewContainer.classList.add("hidden");
        } else if (currentProvider === "gemini") {
            solveBtnText.textContent = "GIẢI ĐỀ BẰNG GEMINI CLOUD (.ENV)";
            solveBtn.style.background = "linear-gradient(135deg, var(--accent-purple), #8b5cf6)";
            modelSelectWrapper.classList.remove("hidden");
            populateModelSelect("gemini");
            singleViewContainer.classList.remove("hidden");
            dualViewContainer.classList.add("hidden");
        } else if (currentProvider === "parallel") {
            solveBtnText.textContent = "CHẠY SONG SONG CẢ 2 (OLLAMA + GEMINI)";
            solveBtn.style.background = "linear-gradient(135deg, #f59e0b, #d97706)";
            modelSelectWrapper.classList.add("hidden");
            singleViewContainer.classList.add("hidden");
            dualViewContainer.classList.remove("hidden");
        }
    }

    function populateModelSelect(prov) {
        modelSelect.innerHTML = "";
        if (prov === "ollama") {
            if (ollamaModelsList.length === 0) {
                const opt = document.createElement("option");
                opt.value = "qwen2.5:7b";
                opt.textContent = "qwen2.5:7b";
                modelSelect.appendChild(opt);
            } else {
                ollamaModelsList.forEach(m => {
                    const opt = document.createElement("option");
                    opt.value = m.name;
                    let label = m.name;
                    if (m.name.includes("qwen2.5:7b")) label += " ⭐ (Khuyên dùng: HSG)";
                    else if (m.name.includes("coder")) label += " 💻 (Code)";
                    opt.textContent = `${label} [${m.size}]`;
                    modelSelect.appendChild(opt);
                });
            }
            modelSelect.value = "qwen2.5:7b";
        } else if (prov === "gemini") {
            const opt1 = document.createElement("option");
            opt1.value = "gemini-flash-latest";
            opt1.textContent = "gemini-flash-latest ⭐ (Tự động chọn Flash tối ưu, ổn định)";
            const opt2 = document.createElement("option");
            opt2.value = "gemini-3.6-flash";
            opt2.textContent = "gemini-3.6-flash (Tốc độ cao, không nghẽn 503)";
            const opt3 = document.createElement("option");
            opt3.value = "gemini-3.7-flash";
            opt3.textContent = "gemini-3.7-flash (Phiên bản mới nhất 2026)";
            const opt4 = document.createElement("option");
            opt4.value = "gemini-pro-latest";
            opt4.textContent = "gemini-pro-latest (Tư duy suy luận sâu)";
            modelSelect.appendChild(opt1);
            modelSelect.appendChild(opt2);
            modelSelect.appendChild(opt3);
            modelSelect.appendChild(opt4);
        }
    }

    // ===== FETCH ENV & KEY STATUS =====
    async function checkEnvAndKeys(populateInput = false) {
        try {
            const res = await fetch("/api/env-status");
            const data = await res.json();
            if (data.gemini_loaded) {
                geminiEnvBadge.textContent = `Gemini .env: ${data.gemini_keys_count} keys sẵn sàng`;
                openKeysModalBtn.className = "btn-keys-status ready";
            } else {
                geminiEnvBadge.textContent = "Gemini: Chưa nạp key (.env)";
                openKeysModalBtn.className = "btn-keys-status";
            }

            // Key modal status & populate textarea
            const keysRes = await fetch("/api/keys");
            const keysData = await keysRes.json();
            const geminiPool = keysData.gemini || {};
            keyStatusSummary.innerHTML = `
                <div><strong>Tổng số key Gemini:</strong> ${geminiPool.total_keys || 0}</div>
                <div><strong>Đang sẵn sàng:</strong> ${geminiPool.active_keys || 0} | <strong>Đang nghỉ hồi phục (429):</strong> ${geminiPool.cooldown_keys || 0}</div>
            `;

            // Tự động điền danh sách key vào textarea để người dùng thấy rõ
            if (populateInput && keysData.gemini_keys && keysData.gemini_keys.length > 0) {
                geminiKeysInput.value = keysData.gemini_keys.join("\n");
            }
        } catch (e) {
            console.error("Lỗi kiểm tra env:", e);
        }
    }

    // Modal Events
    openKeysModalBtn.addEventListener("click", () => {
        checkEnvAndKeys(true);
        keysModal.classList.remove("hidden");
    });

    closeKeysModalBtn.addEventListener("click", () => {
        keysModal.classList.add("hidden");
    });

    reloadEnvBtn.addEventListener("click", async () => {
        try {
            const res = await fetch("/api/env/reload", { method: "POST" });
            const data = await res.json();
            if (data.gemini_keys && data.gemini_keys.length > 0) {
                geminiKeysInput.value = data.gemini_keys.join("\n");
            }
            showToast(`Đã nạp ${data.gemini_keys ? data.gemini_keys.length : 0} keys từ file .env!`);
            checkEnvAndKeys(false);
        } catch (e) {
            showToast("Lỗi nạp lại .env: " + e.message, "error");
        }
    });

    saveKeysBtn.addEventListener("click", async () => {
        const text = geminiKeysInput.value.trim();
        const keys = text.split("\n").map(k => k.trim()).filter(k => k.length > 0);
        if (keys.length === 0) {
            showToast("Vui lòng nhập ít nhất 1 key", "error");
            return;
        }

        try {
            const res = await fetch("/api/keys", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ provider: "gemini", keys: keys })
            });
            const data = await res.json();
            showToast(`Đã lưu ${keys.length} API keys vào .env thành công!`);
            keysModal.classList.add("hidden");
            checkEnvAndKeys(true);
        } catch (e) {
            showToast("Lỗi lưu keys: " + e.message, "error");
        }
    });

    // ===== INIT MODELS & SAMPLES =====
    async function initSystem() {
        try {
            const modelsRes = await fetch("/api/models");
            const modelsData = await modelsRes.json();
            ollamaModelsList = modelsData.ollama_models || [];
            populateModelSelect("ollama");

            const samplesRes = await fetch("/api/samples");
            const samplesJson = await samplesRes.json();
            sampleProblemsData = samplesJson.samples || [];

            await checkEnvAndKeys();
        } catch (e) {
            console.error("Lỗi khởi tạo hệ thống:", e);
        }
    }

    initSystem();

    const DEFAULT_SAMPLES = {
        "subset_sum": {
            title: "Tìm Dãy Con Có Tổng Bằng S (SUBSET SUM)",
            text: "Cho một dãy số nguyên dương A = {a1, a2, ..., an} và một số nguyên dương S.\nYêu cầu: Hãy tìm một dãy con của A có tổng các phần tử đúng bằng S sao cho số lượng phần tử là ít nhất có thể.\n\nDữ liệu vào:\n- Dòng đầu chứa hai số nguyên dương N và S (1 <= N <= 100, 1 <= S <= 10^5).\n- Dòng thứ hai chứa N số nguyên dương a1, a2, ..., an (1 <= ai <= 10^4).\n\nDữ liệu ra:\n- In ra số lượng phần tử ít nhất của dãy con có tổng bằng S. Nếu không có cách chọn nào thỏa mãn, in ra -1.\n\nRàng buộc:\n- Subtask 1 (30% số điểm): N <= 20, S <= 100.\n- Subtask 2 (40% số điểm): N <= 100, S <= 10^4.\n- Subtask 3 (30% số điểm): N <= 100, S <= 10^5.\n\nVí dụ:\nInput:\n5 12\n2 3 5 7 10\nOutput:\n2\n(Giải thích: Chọn 2 phần tử {5, 7} có tổng 5 + 7 = 12 -> 2 phần tử)."
        },
        "max_subarray": {
            title: "Đoạn con có tổng lớn nhất (MAXSUB)",
            text: "Cho một dãy số nguyên A gồm N phần tử: a1, a2, ..., aN.\nMột đoạn con của dãy A là một dãy liên tiếp các phần tử ai, ai+1, ..., aj với 1 <= i <= j <= N.\nTrọng số của một đoạn con là tổng tất cả các phần tử trong đoạn con đó.\nYêu cầu: Hãy tìm đoạn con có trọng số lớn nhất.\n\nDữ liệu vào:\n- Dòng thứ nhất chứa số nguyên N (1 <= N <= 10^6).\n- Dòng thứ hai chứa N số nguyên a1, a2, ..., aN (|ai| <= 10^9).\n\nDữ liệu ra:\n- Một số nguyên duy nhất là trọng số lớn nhất của đoạn con tìm được.\n\nRàng buộc:\n- Subtask 1 (30% số điểm): N <= 500.\n- Subtask 2 (30% số điểm): N <= 5000.\n- Subtask 3 (40% số điểm): N <= 10^6.\n\nVí dụ:\nInput:\n6\n-2 1 -3 4 -1 2\nOutput:\n5\n(Đoạn con [4, -1, 2] có tổng lớn nhất là 4 + (-1) + 2 = 5)."
        },
        "binary_search_wood": {
            title: "Cắt gỗ lấy củi (EKO)",
            text: "Mirko cần chặt một lượng gỗ có tổng chiều dài ít nhất là M mét. Thiết bị của Mirko là một máy cắt gỗ hoạt động như sau: Mirko thiết lập một thông số chiều cao H (mét). Máy sẽ cắt tất cả các cây cao hơn H, phần ngọn cây cao hơn H sẽ bị cắt đứt và rơi xuống đất, phần thân cây có chiều cao <= H sẽ được giữ nguyên.\nMirko muốn tìm chiều cao H nguyên lớn nhất có thể thiết lập sao cho tổng lượng gỗ thu được ít nhất là M mét.\n\nDữ liệu vào:\n- Dòng đầu chứa hai số nguyên dương N và M (1 <= N <= 10^6, 1 <= M <= 2*10^9).\n- Dòng thứ hai chứa N số nguyên dương là chiều cao của N cái cây, mỗi cây có chiều cao không quá 10^9 mét.\n\nDữ liệu ra:\n- Chiều cao nguyên H lớn nhất cần tìm.\n\nGiới hạn:\n- Subtask 1 (20% số điểm): N <= 1000, M <= 10^4, chiều cao cây <= 10^4.\n- Subtask 2 (30% số điểm): N <= 10^5, M <= 10^9.\n- Subtask 3 (50% số điểm): N <= 10^6, M <= 2*10^9.\n\nVí dụ:\nInput:\n4 7\n20 15 10 17\nOutput:\n15"
        }
    };

    // Sample buttons
    document.querySelectorAll(".sample-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            const sampleId = btn.getAttribute("data-sample");
            let sample = sampleProblemsData.find(s => s.id === sampleId);
            if (!sample && DEFAULT_SAMPLES[sampleId]) {
                sample = DEFAULT_SAMPLES[sampleId];
            }
            if (sample) {
                problemInput.value = sample.text;
                problemInput.style.boxShadow = "";
                problemInput.style.borderColor = "";
                updateCharCount();
                showToast(`Đã nạp đề mẫu: ${sample.title}`);
            }
        });
    });

    function updateCharCount() {
        const len = problemInput.value.trim().length;
        charCount.textContent = `${len.toLocaleString()} ký tự`;
    }

    problemInput.addEventListener("input", () => {
        problemInput.style.boxShadow = "";
        problemInput.style.borderColor = "";
        updateCharCount();
    });

    clearTextBtn.addEventListener("click", () => {
        problemInput.value = "";
        updateCharCount();
    });

    pasteBtn.addEventListener("click", async () => {
        try {
            const text = await navigator.clipboard.readText();
            if (text) {
                problemInput.value = text;
                updateCharCount();
                showToast("Đã dán nội dung!");
            }
        } catch (e) {
            showToast("Vui lòng cấp quyền clipboard", "error");
        }
    });

    // Clipboard image paste
    window.addEventListener("paste", async (e) => {
        const items = (e.clipboardData || e.originalEvent.clipboardData).items;
        for (let item of items) {
            if (item.kind === "file" && item.type.startsWith("image/")) {
                const blob = item.getAsFile();
                if (blob) {
                    e.preventDefault();
                    showToast("Đang bóc tách chữ từ ảnh...", "success");
                    await uploadAndProcessFile(blob, "screenshot.png");
                    return;
                }
            }
        }
    });

    // File Drag & Drop
    dropZone.addEventListener("click", () => fileInput.click());
    dropZone.addEventListener("dragover", (e) => { e.preventDefault(); dropZone.classList.add("dragover"); });
    dropZone.addEventListener("dragleave", () => dropZone.classList.remove("dragover"));
    dropZone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropZone.classList.remove("dragover");
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            uploadAndProcessFile(e.dataTransfer.files[0], e.dataTransfer.files[0].name);
        }
    });

    fileInput.addEventListener("change", () => {
        if (fileInput.files && fileInput.files.length > 0) {
            uploadAndProcessFile(fileInput.files[0], fileInput.files[0].name);
        }
    });

    clearFileBtn.addEventListener("click", () => {
        fileStatus.classList.add("hidden");
        fileInput.value = "";
    });

    async function uploadAndProcessFile(file, name) {
        const formData = new FormData();
        formData.append("file", file, name);

        dropZone.style.opacity = "0.5";
        try {
            const res = await fetch("/api/upload", { method: "POST", body: formData });
            const data = await res.json();
            fileName.textContent = data.filename;
            fileType.textContent = (data.file_type || "FILE").toUpperCase();
            fileStatus.classList.remove("hidden");
            if (data.content) {
                problemInput.value = data.content;
                updateCharCount();
                showToast(`Đã đọc ${data.filename}!`);
            }
        } catch (e) {
            showToast("Lỗi đọc file: " + e.message, "error");
        } finally {
            dropZone.style.opacity = "1";
            lucide.createIcons();
        }
    }

    // Tabs
    tabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const tabId = btn.getAttribute("data-tab");
            tabBtns.forEach(b => b.classList.remove("active"));
            tabPanes.forEach(p => p.classList.remove("active"));
            btn.classList.add("active");
            const targetPane = document.getElementById(tabId);
            if (targetPane) targetPane.classList.add("active");
        });
    });

    // ===== SOLVE LOGIC =====
    solveBtn.addEventListener("click", () => {
        if (currentProvider === "parallel") {
            startParallelSolving();
        } else {
            startSingleSolving();
        }
    });

    stopBtn.addEventListener("click", stopSolving);

    function stopSolving() {
        if (currentAbortController) {
            currentAbortController.abort();
            currentAbortController = null;
        }
        if (currentAbortController2) {
            currentAbortController2.abort();
            currentAbortController2 = null;
        }
        finishSolving();
    }

    function finishSolving() {
        solveBtn.classList.remove("hidden");
        stopBtn.classList.add("hidden");
        streamStatus.classList.add("hidden");
        streamStatusLeft.classList.add("hidden");
        streamStatusRight.classList.add("hidden");
        lucide.createIcons();
    }

    // ===== SINGLE SOLVING (Ollama OR Gemini) =====
    async function startSingleSolving() {
        const text = problemInput.value.trim();
        if (!text) {
            problemInput.focus();
            problemInput.style.boxShadow = "0 0 0 2px #ef4444";
            problemInput.style.borderColor = "#ef4444";
            showToast("Vui lòng nhập đề bài hoặc bấm chọn Đề mẫu phía trên!", "error");
            return;
        }
        problemInput.style.boxShadow = "";
        problemInput.style.borderColor = "";

        const selectedModel = modelSelect.value;

        emptyState.classList.add("hidden");
        markdownOutput.classList.remove("hidden");
        markdownOutput.innerHTML = "";
        streamStatus.classList.remove("hidden");
        streamStatusText.textContent = `Đang phân tích bằng [${currentProvider.toUpperCase()}: ${selectedModel}]...`;

        solveBtn.classList.add("hidden");
        stopBtn.classList.remove("hidden");

        fullMarkdownText = "";
        tabBtns[0].click();
        currentAbortController = new AbortController();

        try {
            const res = await fetch("/api/solve", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    problem_text: text,
                    model: selectedModel,
                    provider: currentProvider,
                    mode: "agent",
                    temperature: 0.2
                }),
                signal: currentAbortController.signal
            });

            const reader = res.body.getReader();
            const decoder = new TextDecoder("utf-8");
            let buffer = "";

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split("\n\n");
                buffer = lines.pop();

                for (const line of lines) {
                    if (line.startsWith("data: ")) {
                        const jsonStr = line.slice(6).trim();
                        try {
                            const parsed = JSON.parse(jsonStr);
                            if (parsed.type === "token") {
                                fullMarkdownText += parsed.content;
                                markdownOutput.innerHTML = marked.parse(fullMarkdownText);
                                renderKaTeX(markdownOutput);
                            } else if (parsed.type === "agent_step" && parsed.message) {
                                streamStatusText.textContent = parsed.message;
                            } else if (parsed.type === "done") {
                                break;
                            }
                        } catch (e) {}
                    }
                }
            }

        } catch (err) {
            if (err.name !== "AbortError") {
                showToast(`Lỗi: ${err.message}`, "error");
            }
        } finally {
            finishSolving();
            finalizeSingleView();
        }
    }

    function finalizeSingleView() {
        if (!fullMarkdownText) return;
        markdownOutput.innerHTML = marked.parse(fullMarkdownText);
        renderKaTeX(markdownOutput);
        Prism.highlightAllUnder(markdownOutput);
        extractCodeBlocks(fullMarkdownText);
        extractSubtasks(fullMarkdownText);
    }

    // ===== DUAL PARALLEL SOLVING (Ollama + Gemini song song) =====
    async function startParallelSolving() {
        const text = problemInput.value.trim();
        if (!text) {
            problemInput.focus();
            problemInput.style.boxShadow = "0 0 0 2px #ef4444";
            problemInput.style.borderColor = "#ef4444";
            showToast("Vui lòng nhập đề bài hoặc bấm chọn Đề mẫu phía trên!", "error");
            return;
        }
        problemInput.style.boxShadow = "";
        problemInput.style.borderColor = "";

        solveBtn.classList.add("hidden");
        stopBtn.classList.remove("hidden");

        streamStatusLeft.classList.remove("hidden");
        streamStatusRight.classList.remove("hidden");

        markdownOutputLeft.innerHTML = "";
        markdownOutputRight.innerHTML = "";
        fullMarkdownTextLeft = "";
        fullMarkdownTextRight = "";

        currentAbortController = new AbortController();
        currentAbortController2 = new AbortController();

        // Stream 1: Ollama
        const runOllama = async () => {
            try {
                const res = await fetch("/api/solve", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        problem_text: text,
                        model: "qwen2.5:7b",
                        provider: "ollama",
                        mode: "agent",
                        temperature: 0.2
                    }),
                    signal: currentAbortController.signal
                });

                const reader = res.body.getReader();
                const decoder = new TextDecoder("utf-8");
                let buffer = "";

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;
                    buffer += decoder.decode(value, { stream: true });
                    const lines = buffer.split("\n\n");
                    buffer = lines.pop();

                    for (const line of lines) {
                        if (line.startsWith("data: ")) {
                            try {
                                const parsed = JSON.parse(line.slice(6).trim());
                                if (parsed.type === "token") {
                                    fullMarkdownTextLeft += parsed.content;
                                    markdownOutputLeft.innerHTML = marked.parse(fullMarkdownTextLeft);
                                    renderKaTeX(markdownOutputLeft);
                                }
                            } catch (e) {}
                        }
                    }
                }
            } catch (e) {
                if (e.name !== "AbortError") {
                    markdownOutputLeft.innerHTML += `<div style="color:var(--accent-red)">[Lỗi Ollama: ${e.message}]</div>`;
                }
            } finally {
                streamStatusLeft.classList.add("hidden");
                Prism.highlightAllUnder(markdownOutputLeft);
            }
        };

        // Stream 2: Gemini
        const runGemini = async () => {
            try {
                const res = await fetch("/api/solve", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        problem_text: text,
                        model: "gemini-3.6-flash",
                        provider: "gemini",
                        mode: "agent",
                        temperature: 0.2
                    }),
                    signal: currentAbortController2.signal
                });

                const reader = res.body.getReader();
                const decoder = new TextDecoder("utf-8");
                let buffer = "";

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;
                    buffer += decoder.decode(value, { stream: true });
                    const lines = buffer.split("\n\n");
                    buffer = lines.pop();

                    for (const line of lines) {
                        if (line.startsWith("data: ")) {
                            try {
                                const parsed = JSON.parse(line.slice(6).trim());
                                if (parsed.type === "token") {
                                    fullMarkdownTextRight += parsed.content;
                                    markdownOutputRight.innerHTML = marked.parse(fullMarkdownTextRight);
                                    renderKaTeX(markdownOutputRight);
                                }
                            } catch (e) {}
                        }
                    }
                }
            } catch (e) {
                if (e.name !== "AbortError") {
                    markdownOutputRight.innerHTML += `<div style="color:var(--accent-red)">[Lỗi Gemini: ${e.message}]</div>`;
                }
            } finally {
                streamStatusRight.classList.add("hidden");
                Prism.highlightAllUnder(markdownOutputRight);
            }
        };

        // Run both concurrently
        await Promise.allSettled([runOllama(), runGemini()]);
        finishSolving();
        showToast("Đã hoàn tất giải đề song song trên cả 2 mô hình!");
    }

    function renderKaTeX(element) {
        if (window.renderMathInElement) {
            renderMathInElement(element, {
                delimiters: [
                    { left: "$$", right: "$$", display: true },
                    { left: "$", right: "$", display: false },
                    { left: "\\(", right: "\\)", display: false },
                    { left: "\\[", right: "\\]", display: true }
                ],
                throwOnError: false
            });
        }
    }

    function extractCodeBlocks(markdown) {
        const codeBlockRegex = /```(cpp|c\+\+|python|py)?\s*([\s\S]*?)```/g;
        let match;
        let foundCpp = "";
        let foundPy = "";
        let foundGen = "";

        while ((match = codeBlockRegex.exec(markdown)) !== null) {
            const lang = (match[1] || "").toLowerCase();
            const code = match[2].trim();

            if ((lang === "cpp" || lang === "c++") && !foundCpp) {
                foundCpp = code;
            } else if (lang === "python" || lang === "py") {
                if (!foundPy) foundPy = code;
                else if (!foundGen) foundGen = code;
            }
        }

        if (foundCpp) {
            cppCode.textContent = foundCpp;
            Prism.highlightElement(cppCode);
        }
        if (foundPy) {
            pyCode.textContent = foundPy;
            Prism.highlightElement(pyCode);
        }
        if (foundGen) {
            genScriptCode.textContent = foundGen;
            Prism.highlightElement(genScriptCode);
        }

        const testSectionMatch = markdown.match(/##\s*6[\s\S]*?(?=##\s*7|$)/i);
        if (testSectionMatch) {
            testsAnalysis.innerHTML = marked.parse(testSectionMatch[0]);
            renderKaTeX(testsAnalysis);
        }
    }

    function extractSubtasks(markdown) {
        const subtasksMatch = markdown.match(/##\s*2[\s\S]*?(?=##\s*4|$)/i);
        if (subtasksMatch) {
            subtasksContent.innerHTML = marked.parse(subtasksMatch[0]);
            renderKaTeX(subtasksContent);
        } else {
            subtasksContent.innerHTML = marked.parse(markdown);
            renderKaTeX(subtasksContent);
        }
    }

    // Copy actions
    copyAllBtn.addEventListener("click", () => {
        if (!fullMarkdownText) return showToast("Chưa có lời giải!", "error");
        navigator.clipboard.writeText(fullMarkdownText).then(() => showToast("Đã sao chép toàn bộ!"));
    });

    copyCppBtn.addEventListener("click", () => {
        navigator.clipboard.writeText(cppCode.textContent).then(() => showToast("Đã sao chép C++!"));
    });

    downloadCppBtn.addEventListener("click", () => downloadFile("solution.cpp", cppCode.textContent));

    copyPyBtn.addEventListener("click", () => {
        navigator.clipboard.writeText(pyCode.textContent).then(() => showToast("Đã sao chép Python!"));
    });

    downloadPyBtn.addEventListener("click", () => downloadFile("solution.py", pyCode.textContent));

    copyGenBtn.addEventListener("click", () => {
        navigator.clipboard.writeText(genScriptCode.textContent).then(() => showToast("Đã sao chép bộ sinh test!"));
    });

    downloadGenBtn.addEventListener("click", () => downloadFile("test_gen.py", genScriptCode.textContent));

    copyDualLeftBtn.addEventListener("click", () => {
        if (!fullMarkdownTextLeft) return showToast("Chưa có nội dung!", "error");
        navigator.clipboard.writeText(fullMarkdownTextLeft).then(() => showToast("Đã sao chép lời giải Ollama!"));
    });

    copyDualRightBtn.addEventListener("click", () => {
        if (!fullMarkdownTextRight) return showToast("Chưa có nội dung!", "error");
        navigator.clipboard.writeText(fullMarkdownTextRight).then(() => showToast("Đã sao chép lời giải Gemini!"));
    });

    function downloadFile(filename, text) {
        const blob = new Blob([text], { type: "text/plain;charset=utf-8" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        showToast(`Đã tải xuống ${filename}!`);
    }
});
