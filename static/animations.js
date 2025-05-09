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
    const numberOfParticles = 100; // 初始设定的粒子数量

    class Particle {
        constructor(x, y) {
            this.x = x !== undefined ? x : Math.random() * canvas.width;
            this.y = y !== undefined ? y : Math.random() * canvas.height;
            this.size = Math.random() * 2 + 0.5; // 初始大小
            this.speedX = Math.random() * 1 - 0.5; // 初始 X轴速度
            this.speedY = Math.random() * 1 - 0.5; // 初始 Y轴速度
            // 初始蓝紫色系粒子
            this.color = `rgba(${Math.random() * 100 + 100}, ${Math.random() * 50 + 50}, ${Math.random() * 100 + 155}, ${Math.random() * 0.5 + 0.3})`;
        }
        update() {
            this.x += this.speedX;
            this.y += this.speedY;

            // 边界处理：粒子移出画布后反弹
            if (this.x < 0 || this.x > canvas.width) {
                this.speedX *= -1;
            }
            if (this.y < 0 || this.y > canvas.height) {
                this.speedY *= -1;
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
            particlesArray.push(new Particle());
        }
    }
    initParticles();

    function animateParticles() {
        ctx.clearRect(0, 0, canvas.width, canvas.height); // 清晰的粒子，每次都清除画布
        for (let i = 0; i < particlesArray.length; i++) {
            particlesArray[i].update();
            particlesArray[i].draw();
        }

        // 连接粒子形成流线 (初始版本包含这个)
        for (let i = 0; i < particlesArray.length; i++) {
            for (let j = i; j < particlesArray.length; j++) {
                const dx = particlesArray[i].x - particlesArray[j].x;
                const dy = particlesArray[i].y - particlesArray[j].y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                if (distance < 120) { // 连接距离阈值
                    ctx.beginPath();
                    // 线条颜色也应与粒子协调，例如使用更淡或有透明度的同色系
                    ctx.strokeStyle = `rgba(170, 100, 255, ${Math.max(0, (1 - distance/120) * 0.5)})`; // 示例：淡紫色线条
                    ctx.lineWidth = 0.4;
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

// 确保在 DOM 加载完毕后执行动画初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initBackgroundAnimation);
} else {
    initBackgroundAnimation();
}