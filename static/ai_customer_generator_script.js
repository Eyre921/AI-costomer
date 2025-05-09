document.addEventListener('DOMContentLoaded', () => {
    const productInfoTextarea = document.getElementById('product-info');
    const generateButton = document.getElementById('generate-button');
    const numProfilesInput = document.getElementById('num-profiles');
    const numQuestionsInput = document.getElementById('num-questions');

    const loadingSpinner = document.getElementById('loading-spinner');
    const errorBox = document.getElementById('error-box');

    const productSummaryContainer = document.getElementById('product-summary-container');
    const productSummaryText = document.getElementById('product-summary-text');
    const profilesDisplay = document.getElementById('customer-profiles-display');

    const questionsDisplayContainer = document.getElementById('questions-display-container');
    const selectedProfileNameHeader = document.getElementById('selected-profile-name-header');
    const b2bQuestionsUl = document.getElementById('b2b-questions-ul');
    const b2cQuestionsUl = document.getElementById('b2c-questions-ul');

    let currentProfilesData = [];

    generateButton.addEventListener('click', async () => {
        const productDocument = productInfoTextarea.value.trim();
        const numProfiles = parseInt(numProfilesInput.value);
        const numQuestions = parseInt(numQuestionsInput.value);

        if (!productDocument) { displayError("请输入产品信息！"); return; }
        if (isNaN(numProfiles) || numProfiles < 1 || numProfiles > 10) { displayError("画像数量必须在1到10之间！"); return; }
        if (isNaN(numQuestions) || numQuestions < 2 || numQuestions > 10) { displayError("每个画像的总问题数必须在2到10之间！"); return; }

        loadingSpinner.style.display = 'block';
        generateButton.disabled = true;
        clearResults();
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
                } catch (e) { errorDetail = `服务器错误 ${response.status}: ${response.statusText}`; }
                throw new Error(errorDetail);
            }
            const data = await response.json();
            renderResults(data);
        } catch (error) {
            console.error('Error fetching AI customer data:', error);
            displayError(error.message || '生成数据时发生未知错误。');
        } finally {
            loadingSpinner.style.display = 'none';
            generateButton.disabled = false;
        }
    });

    function displayError(message) {
        errorBox.textContent = message;
        errorBox.style.display = 'block';
    }
    function hideError() { errorBox.style.display = 'none'; }

    function clearResults() {
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
        if (data.product_summary) {
            productSummaryText.textContent = data.product_summary;
            productSummaryContainer.style.display = 'block';
        }
        currentProfilesData = data.customer_profiles || [];
        profilesDisplay.innerHTML = '';

        if (currentProfilesData.length === 0) {
            profilesDisplay.innerHTML = '<p>未能生成客户画像。</p>';
            return;
        }
        currentProfilesData.forEach((profile, index) => {
            const card = document.createElement('div');
            card.classList.add('profile-card');
            card.dataset.profileIndex = index;
            let concernsHTML = profile.main_concerns && profile.main_concerns.length > 0
                ? `<strong>主要关注点:</strong> ${profile.main_concerns.join(', ')}<br>` : '';

            card.innerHTML = `
                <h3>${profile.name || '未命名画像'}</h3>
                <p>${profile.description || '无详细描述'}</p>
                <p>
                    ${profile.country_region ? `<strong>国家/地区:</strong> ${profile.country_region}<br>` : ''}
                    ${profile.occupation ? `<strong>职业:</strong> ${profile.occupation}<br>` : ''}
                    ${profile.cognitive_level ? `<strong>认知水平:</strong> ${profile.cognitive_level}<br>` : ''}
                    ${concernsHTML}
                    ${profile.potential_needs ? `<strong>潜在需求:</strong> ${profile.potential_needs}<br>` : ''}
                    ${profile.cultural_background_summary ? `<strong>文化背景:</strong> ${profile.cultural_background_summary}` : ''}
                </p>
                <small>B2B问题: ${profile.b2b_questions ? profile.b2b_questions.length : 0} | B2C问题: ${profile.b2c_questions ? profile.b2c_questions.length : 0}</small>
            `;
            card.addEventListener('click', () => {
                renderQuestionsForProfile(index);
                document.querySelectorAll('.profile-card').forEach(c => c.classList.remove('active'));
                card.classList.add('active');
            });
            profilesDisplay.appendChild(card);
        });
    }

    function renderQuestionsForProfile(profileIndex) {
        const profile = currentProfilesData[profileIndex];
        if (!profile) return;

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
        questionsDisplayContainer.style.display = 'block'; // 显示问题区域
    }
});