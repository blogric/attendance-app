document.addEventListener("DOMContentLoaded", () => {

    if ("Notification" in window) {
        Notification.requestPermission();
    }

    const today = new Date().toISOString().split("T")[0];
    const saved = localStorage.getItem("lastMarked");

    if (saved !== today) {
        setTimeout(() => {
            if (Notification.permission === "granted") {
                new Notification("Adnan - Attendance Reminder", {
                    body: "Please mark your attendance today",
                });
            } else {
                alert("Mark your attendance today");
            }
        }, 2000);
    }
});
