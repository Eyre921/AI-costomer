// static/animations.js

function initBackgroundAnimation() {
    const canvas = document.getElementById('background-animation-canvas');
    if (!canvas) {
        console.warn('Background canvas not found. Skipping animation.');
        return;
    }
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    let particlesArray = [];
    const numberOfParticles = 120; // 可以适当增加粒子数量

    class Particle {
        constructor(x, y) {
            this.x = x;
            this.y = y;
            this.size = Math.random() * 2.5 + 0.5; // 粒子大小范围调整
            this.speedX = Math.random() * 0.8 - 0.4; // 速度可以稍微慢一点
            this.speedY = Math.random() * 0.8 - 0.4;
            // 调整为蓝绿色系粒子，R G B: (0-100, 100-255, 100-255) 或 (100-200, 200-255, 0-100)
            // 更多青色/绿色粒子
            const r = Math.random() * 100; // 红色分量较低
            const g = Math.random() * 155 + 100; // 绿色分量较高
            const b = Math.random() * 155 + 100; // 蓝色分量较高
            this.color = `rgba(${r}, ${g}, ${b}, ${Math.random() * 0.4 + 0.2})`; // 透明度降低一点
        }
        update() {
            this.x += this.speedX;
            this.y += this.speedY;

            if (this.x < -this.size || this.x > canvas.width + this.size || this.y < -this.size || this.y > canvas.height + this.size) {
                // 粒子完全移出画布时，在对侧随机位置重新生成
                if (Math.random() > 0.5) { // 50% 概率从 X 轴两侧出现
                    this.x = this.speedX > 0 ? -this.size : canvas.width + this.size;
                    this.y = Math.random() * canvas.height;
                } else { // 50% 概率从 Y 轴两侧出现
                    this.y = this.speedY > 0 ? -this.size : canvas.height + this.size;
                    this.x = Math.random() * canvas.width;
                }
                 // 可以稍微改变一下粒子的其他属性
                this.size = Math.random() * 2.5 + 0.5;
                this.speedX = Math.random() * 0.8 - 0.4;
                this.speedY = Math.random() * 0.8 - 0.4;
            }
        }
        draw() {
            ctx.fillStyle = this.color;
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    function initParticles() {
        particlesArray = [];
        for (let i = 0; i < numberOfParticles; i++) {
            const x = Math.random() * canvas.width;
            const y = Math.random() * canvas.height;
            particlesArray.push(new Particle(x, y));
        }
    }
    initParticles();

    function animateParticles() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        for (let i = 0; i < particlesArray.length; i++) {
            particlesArray[i].update();
            particlesArray[i].draw();
        }

        // 连接粒子形成流线 (线条颜色也应调整)
        for (let i = 0; i < particlesArray.length; i++) {
            for (let j = i; j < particlesArray.length; j++) {
                const dx = particlesArray[i].x - particlesArray[j].x;
                const dy = particlesArray[i].y - particlesArray[j].y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                if (distance < 130) { // 连接距离阈值
                    // 调整线条颜色为淡青色或淡蓝色
                    const r = Math.random() * 50 + 100; // R: 100-150
                    const g = Math.random() * 100 + 150; // G: 150-255
                    const b = Math.random() * 100 + 150; // B: 150-255
                    ctx.beginPath();
                    ctx.strokeStyle = `rgba(${r}, ${g}, ${b}, ${Math.max(0, (1 - distance/130) * 0.4)})`; // 调整透明度和亮度
                    ctx.lineWidth = 0.3;
                    ctx.moveTo(particlesArray[i].x, particlesArray[i].y);
                    ctx.lineTo(particlesArray[j].x, particlesArray[j].y);
                    ctx.stroke();
                }
            }
        }
        requestAnimationFrame(animateParticles);
    }
    animateParticles();

    window.addEventListener('resize', () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        initParticles();
    });
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initBackgroundAnimation);
} else {
    initBackgroundAnimation();
}