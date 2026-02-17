(function () {
    const INTERVAL = 500;   // 2 seconds
    const MAX_TIME = 15000; // 15 seconds
    let elapsed = 0;

    const timer = setInterval(() => {
        const badge = document.getElementById('notif-count');
        console.log(badge)

        if (badge) {
            console.log('notif-count found');

            fetch('/portal/get_notification_count', {
                method: 'GET',
                credentials: 'same-origin'
            })
            .then(res => res.json())
            .then(data => {
                console.log('notif data:', data);
                if (data.count && data.count > 0) {
                    badge.style.display = 'flex';
                    badge.textContent = data.count;
                }
            })
            .catch(err => console.error(err));

            clearInterval(timer); // ✅ stop once done
            return;
        }

        elapsed += INTERVAL;
        if (elapsed >= MAX_TIME) {
            console.log('notif-count not found, stopping retries');
            clearInterval(timer); // ⛔ stop after 15s
        }
    }, INTERVAL);
})();
