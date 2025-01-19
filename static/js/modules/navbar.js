// Initialize Notifications Button
function initNotificationsButton() {
    console.log("Initializing notifications button...");
    $(document).on("click", ".notifications-button", function () {
        alert("Notifications clicked!");
    });
}

// Initialize Dark Mode Toggle
function initDarkModeToggle() {
    console.log("Initializing dark mode toggle...");
    const htmlElement = $("html");
    const savedTheme = localStorage.getItem("theme");

    // Initialize theme based on localStorage
    htmlElement.toggleClass("dark", savedTheme === "dark");

    $(document).on("click", "#themeToggle", function () {
        const isDarkMode = htmlElement.toggleClass("dark").hasClass("dark");
        localStorage.setItem("theme", isDarkMode ? "dark" : "light");
        console.log("Dark mode status:", isDarkMode);
    });
}

// Initialize Profile Dropdown
function initProfileDropdown() {
    console.log("Initializing profile dropdown...");
    $(document).on("click", "#profileDropdownButton", function (e) {
        e.stopPropagation();
        $("#profileDropdown").toggleClass("hidden");
    });

    // Close dropdown when clicking outside
    $(document).on("click", function () {
        $("#profileDropdown").addClass("hidden");
    });
}

// Initialize all functions
function initAll() {
    if ($(".notifications-button").length) initNotificationsButton();
    if ($("#themeToggle").length) initDarkModeToggle();
    if ($("#profileDropdownButton").length) initProfileDropdown();
}

// Automatically execute all functions when the script loads
console.log("Executing navbar.js...");
initAll();
