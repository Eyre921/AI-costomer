document.addEventListener('DOMContentLoaded', () => {
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    // const streamModeCheckbox = document.getElementById('stream-mode'); // 移除或注释掉，因为后端只支持非流式

    // 初始化消息历史，可以包含一个初始的系统消息（如果外部API支持或需要）
    // 对于 SiliconFlow，system message 是可以的
    let messagesHistory = [
        // { role: "system", content: "You are a helpful AI assistant." } // 根据需要保留或移除
    ];

    function addMessageToChatBox(role, content) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', role === 'user' ? 'user-message' : 'assistant-message');

        let formattedContent = content.replace(/\n/g, '<br>');
        messageDiv.innerHTML = formattedContent;

        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
        return messageDiv;
    }

    async function sendMessage() {
        const userText = userInput.value.trim();
        if (userText === '') return;

        addMessageToChatBox('user', userText);
        messagesHistory.push({ role: 'user', content: userText }); // 只添加用户自己的消息到history
        userInput.value = '';
        sendButton.disabled = true;

        // const stream = streamModeCheckbox.checked; // 移除或注释掉

        // !! 重要：替换为您的目标API支持的有效模型名称 !!
        const modelForExternalAPI = "deepseek-ai/DeepSeek-V3"; // 例如: "deepseek-ai/DeepSeek-V2"

        try {
            const response = await fetch('/v1/chat/completions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    model: modelForExternalAPI, // 使用为外部API指定的模型名称
                    messages: messagesHistory, // 发送当前干净的对话历史
                    // stream: false, // 后端代理会处理，客户端可不传或传false
                    // 在这里可以添加其他需要的参数，例如 temperature, max_tokens 等
                    // temperature: 0.7,
                    max_tokens: 1024, // 示例
                    // frequency_penalty, enable_thinking 等其他参数也可以在这里添加
                }),
            });

            // 清空之前的错误信息（如果适用）
            const existingErrorMessages = chatBox.querySelectorAll('.error-message');
            existingErrorMessages.forEach(el => el.remove());

            if (!response.ok) {
                let errorData;
                try {
                    errorData = await response.json(); // 尝试解析JSON错误体
                } catch (e) {
                    errorData = { detail: `HTTP error ${response.status}. No JSON response.` };
                }
                // 在聊天框中显示错误，但不添加到 messagesHistory
                addMessageToChatBox('assistant error-message', `错误: ${errorData.detail || response.statusText || '未知错误'}`);
                // messagesHistory.push(...); // 不再将错误信息添加到 history
                return;
            }

            const data = await response.json(); // 因为现在只处理非流式

            if (data.choices && data.choices.length > 0) {
                const assistantText = data.choices[0].message.content;
                addMessageToChatBox('assistant', assistantText);
                // 将AI的有效回复添加到 history
                messagesHistory.push({ role: 'assistant', content: assistantText });
            } else {
                addMessageToChatBox('assistant error-message', 'AI未能生成有效回复。');
            }

        } catch (error) { // 网络错误或其他 fetch 错误
            console.error('发送消息时出错:', error);
            const existingErrorMessages = chatBox.querySelectorAll('.error-message');
            existingErrorMessages.forEach(el => el.remove());
            addMessageToChatBox('assistant error-message', `无法连接到服务: ${error.message}`);
            // messagesHistory.push(...); // 不再将错误信息添加到 history
        } finally {
            sendButton.disabled = false;
            userInput.focus();
        }
    }

    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            sendMessage();
        }
    });

    // 可以在页面加载时清除 messagesHistory 或从 localStorage 加载等
    // 初始的系统消息，如果需要，在 messagesHistory 数组定义时添加
    if (messagesHistory.length === 0 && chatBox.children.length === 0) { // 避免重复添加欢迎语
        // addMessageToChatBox('assistant', '你好！我是AI代理助手。');
        // messagesHistory.push({ role: 'assistant', content: '你好！我是AI代理助手。'}); // 欢迎语也应是有效对话的一部分
    }
});