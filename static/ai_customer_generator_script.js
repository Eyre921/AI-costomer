// static/ai_customer_generator_script.js
document.addEventListener('DOMContentLoaded', () => {
    const productInfoTextarea = document.getElementById('product-info');
    const generateButton = document.getElementById('generate-button');
    const numProfilesInput = document.getElementById('num-profiles');
    const numQuestionsInput = document.getElementById('num-questions');

    const loadingSpinner = document.getElementById('loading-spinner');
    const errorBox = document.getElementById('error-box');

    // 获取结果区域的引用
    const resultsSection = document.getElementById('results-section');
    const productSummaryContainer = document.getElementById('product-summary-container');
    const productSummaryText = document.getElementById('product-summary-text');
    const profilesDisplay = document.getElementById('customer-profiles-display');

    const questionsDisplayContainer = document.getElementById('questions-display-container');
    const selectedProfileNameHeader = document.getElementById('selected-profile-name-header');
    const b2bQuestionsUl = document.getElementById('b2b-questions-ul');
    const b2cQuestionsUl = document.getElementById('b2c-questions-ul');

    let currentProfilesData = [];

    // --- 点击特效 (假设 createRipple 函数已存在) ---
    function createRipple(event) {
        const button = event.currentTarget;
        const existingRipple = button.querySelector(".ripple");
        if(existingRipple) {
            existingRipple.remove();
        }
        const circle = document.createElement("span");
        const diameter = Math.max(button.clientWidth, button.clientHeight);
        const radius = diameter / 2;
        circle.style.width = circle.style.height = `${diameter}px`;
        const rect = button.getBoundingClientRect();
        circle.style.left = `${event.clientX - rect.left - radius}px`;
        circle.style.top = `${event.clientY - rect.top - radius}px`;
        circle.classList.add("ripple");
        button.appendChild(circle);
        circle.addEventListener('animationend', () => {
            circle.remove();
        });
    }

    generateButton.addEventListener('click', async (event) => {
        createRipple(event);

        const productDocument = productInfoTextarea.value.trim();
        const numProfiles = parseInt(numProfilesInput.value);
        const numQuestions = parseInt(numQuestionsInput.value);

        if (!productDocument) { displayError("请输入产品信息！"); return; }
        if (isNaN(numProfiles) || numProfiles < 1 || numProfiles > 10) { displayError("画像数量必须在1到10之间！"); return; }
        if (isNaN(numQuestions) || numQuestions < 2 || numQuestions > 10) { displayError("每个画像的总问题数必须在2到10之间！"); return; }

        loadingSpinner.style.display = 'block';
        generateButton.disabled = true;
        clearResults(); // clearResults 会隐藏 resultsSection
        hideError();

        try {
            const response = await fetch('/v1/generate_ai_customer_data', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', },
                body: JSON.stringify({
                    product_document: productDocument,
                    num_customer_profiles: numProfiles,
                    num_questions_per_profile: numQuestions
                }),
            });

            if (!response.ok) {
                let errorDetail = "请求失败。";
                try {
                    const errorData = await response.json();
                    errorDetail = errorData.detail || `服务器错误 ${response.status}`;
                    if (typeof errorData.detail === 'object') {
                        errorDetail = JSON.stringify(errorData.detail);
                    }
                } catch (e) { errorDetail = `服务器错误 ${response.status}: ${response.statusText}`; }
                throw new Error(errorDetail);
            }
            const data = await response.json();
            resultsSection.style.display = 'block'; // 显示结果区域
            renderResults(data);
        } catch (error) {
            console.error('Error fetching AI customer data:', error);
            displayError(error.message || '生成数据时发生未知错误。');
            resultsSection.style.display = 'none'; // 出错时确保结果区域仍隐藏
        } finally {
            loadingSpinner.style.display = 'none';
            generateButton.disabled = false;
        }
    });

    function displayError(message) {
        errorBox.textContent = message;
        errorBox.style.display = 'block';
    }
    function hideError() {
        errorBox.style.display = 'none';
    }

    function clearResults() {
        if(resultsSection) resultsSection.style.display = 'none'; // 隐藏整个结果区域
        productSummaryText.textContent = '';
        productSummaryContainer.style.display = 'none';
        profilesDisplay.innerHTML = '';
        b2bQuestionsUl.innerHTML = '';
        b2cQuestionsUl.innerHTML = '';
        selectedProfileNameHeader.textContent = '';
        questionsDisplayContainer.style.display = 'none';
        currentProfilesData = [];
    }

    function renderResults(data) {
        // productSummaryContainer 和 questionsDisplayContainer 的显示逻辑由其内容决定
        // resultsSection 已在调用此函数前设为 'block'

        if (data.product_summary) {
            productSummaryText.textContent = data.product_summary;
            productSummaryContainer.style.display = 'block';
        } else {
            productSummaryContainer.style.display = 'none';
        }

        currentProfilesData = data.customer_profiles || [];
        profilesDisplay.innerHTML = '';

        if (currentProfilesData.length === 0) {
            profilesDisplay.innerHTML = '<p style="color: #ffcdd2; text-align: center;">未能生成客户画像。</p>';
            questionsDisplayContainer.style.display = 'none';
            return; // 如果没有画像，直接返回，不尝试渲染第一个画像的问题
        }

        currentProfilesData.forEach((profile, index) => {
            const card = document.createElement('div');
            card.classList.add('profile-card');
            card.dataset.profileIndex = index;
            let concernsHTML = profile.main_concerns && profile.main_concerns.length > 0
                ? `<p><strong>主要关注点:</strong> ${profile.main_concerns.join(', ')}</p>` : '';

            card.innerHTML = `
                <h3>${profile.name || '未命名画像'}</h3>
                <p>${profile.description || '无详细描述'}</p>
                ${profile.country_region ? `<p><strong>国家/地区:</strong> ${profile.country_region}</p>` : ''}
                ${profile.occupation ? `<p><strong>职业:</strong> ${profile.occupation}</p>` : ''}
                ${profile.cognitive_level ? `<p><strong>认知水平:</strong> ${profile.cognitive_level}</p>` : ''}
                ${concernsHTML}
                ${profile.potential_needs ? `<p><strong>潜在需求:</strong> ${profile.potential_needs}</p>` : ''}
                ${profile.cultural_background_summary ? `<p><strong>文化背景:</strong> ${profile.cultural_background_summary}</p>` : ''}
                <small>B2B问题: ${profile.b2b_questions ? profile.b2b_questions.length : 0} | B2C问题: ${profile.b2c_questions ? profile.b2c_questions.length : 0}</small>
            `;

            card.addEventListener('click', (event) => {
                document.querySelectorAll('.profile-card').forEach(c => c.classList.remove('active'));
                card.classList.add('active');
                renderQuestionsForProfile(index);
            });
            profilesDisplay.appendChild(card);
        });

        if(currentProfilesData.length > 0){
            const firstCard = profilesDisplay.querySelector('.profile-card');
            if(firstCard){
                firstCard.classList.add('active');
                renderQuestionsForProfile(0);
            }
        } else {
            questionsDisplayContainer.style.display = 'none';
        }
    }

    function renderQuestionsForProfile(profileIndex) {
        const profile = currentProfilesData[profileIndex];
        if (!profile) {
            questionsDisplayContainer.style.display = 'none';
            return;
        }

        selectedProfileNameHeader.textContent = `“${profile.name || '该画像'}” 可能提出的问题:`;
        b2bQuestionsUl.innerHTML = '';
        b2cQuestionsUl.innerHTML = '';

        if (profile.b2b_questions && profile.b2b_questions.length > 0) {
            profile.b2b_questions.forEach(question => {
                const li = document.createElement('li');
                li.textContent = question.text;
                b2bQuestionsUl.appendChild(li);
            });
        } else {
            b2bQuestionsUl.innerHTML = '<li>未能生成B2B问题。</li>';
        }

        if (profile.b2c_questions && profile.b2c_questions.length > 0) {
            profile.b2c_questions.forEach(question => {
                const li = document.createElement('li');
                li.textContent = question.text;
                b2cQuestionsUl.appendChild(li);
            });
        } else {
            b2cQuestionsUl.innerHTML = '<li>未能生成B2C问题。</li>';
        }
        // 确保 questionsDisplayContainer 在有内容时是可见的
        // （它现在是 results-section 的子元素，results-section 的显示已控制）
        // 如果 questionsDisplayContainer 内部还有独立的 display:none 逻辑，这里可以强制显示
        questionsDisplayContainer.style.display = 'block';
    }
});