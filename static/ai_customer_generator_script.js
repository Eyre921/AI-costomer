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
    const questionsDisplay = document.getElementById('questions-display');
    const questionsHeader = document.getElementById('questions-header');
    const questionsUl = document.getElementById('questions-ul');

    let currentProfilesData = []; // To store fetched profiles

    generateButton.addEventListener('click', async () => {
        const productDocument = productInfoTextarea.value.trim();
        const numProfiles = parseInt(numProfilesInput.value);
        const numQuestions = parseInt(numQuestionsInput.value);

        if (!productDocument) {
            displayError("请输入产品信息！");
            return;
        }
        if (isNaN(numProfiles) || numProfiles < 1 || numProfiles > 10) {
            displayError("画像数量必须在1到10之间！");
            return;
        }
        if (isNaN(numQuestions) || numQuestions < 3 || numQuestions > 10) {
            displayError("每个画像的问题数必须在3到10之间！");
            return;
        }


        loadingSpinner.style.display = 'block';
        generateButton.disabled = true;
        clearResults();
        hideError();

        try {
            const response = await fetch('/v1/generate_ai_customer_data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    product_document: productDocument,
                    num_customer_profiles: numProfiles,
                    num_questions_per_profile: numQuestions
                }),
            });

            if (!response.ok) {
                let errorDetail = "请求失败，请稍后再试。";
                try {
                    const errorData = await response.json();
                    errorDetail = errorData.detail || `服务器错误 ${response.status}`;
                } catch (e) {
                    // Failed to parse JSON, use status text
                    errorDetail = `服务器错误 ${response.status}: ${response.statusText}`;
                }
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

    function hideError() {
        errorBox.style.display = 'none';
    }

    function clearResults() {
        productSummaryText.textContent = '';
        productSummaryContainer.style.display = 'none';
        profilesDisplay.innerHTML = '';
        questionsUl.innerHTML = '';
        questionsHeader.textContent = '请选择一个客户画像以查看其可能提出的问题';
        questionsDisplay.style.display = 'none';
        currentProfilesData = [];
    }

    function renderResults(data) {
        if (data.product_summary) {
            productSummaryText.textContent = data.product_summary;
            productSummaryContainer.style.display = 'block';
        }

        currentProfilesData = data.customer_profiles || [];
        profilesDisplay.innerHTML = ''; // Clear previous profiles

        if (currentProfilesData.length === 0) {
            profilesDisplay.innerHTML = '<p>未能生成客户画像。</p>';
            return;
        }

        currentProfilesData.forEach((profile, index) => {
            const card = document.createElement('div');
            card.classList.add('profile-card');
            card.dataset.profileIndex = index; // Store index for click handling

            let concernsHTML = profile.main_concerns && profile.main_concerns.length > 0
                ? `<strong>主要关注点:</strong> ${profile.main_concerns.join(', ')}<br>`
                : '';

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
                <small>包含 ${profile.questions ? profile.questions.length : 0} 个问题</small>
            `;
            card.addEventListener('click', () => {
                renderQuestionsForProfile(index);
                // Highlight active card
                document.querySelectorAll('.profile-card').forEach(c => c.classList.remove('active'));
                card.classList.add('active');
            });
            profilesDisplay.appendChild(card);
        });
    }

    function renderQuestionsForProfile(profileIndex) {
        const profile = currentProfilesData[profileIndex];
        if (!profile) return;

        questionsHeader.textContent = `“${profile.name || '该画像'}” 可能提出的问题:`;
        questionsUl.innerHTML = ''; // Clear previous questions

        if (profile.questions && profile.questions.length > 0) {
            profile.questions.forEach(question => {
                const li = document.createElement('li');
                li.textContent = question.text;
                questionsUl.appendChild(li);
            });
        } else {
            questionsUl.innerHTML = '<li>此画像没有生成具体问题。</li>';
        }
        questionsDisplay.style.display = 'block';
    }
});