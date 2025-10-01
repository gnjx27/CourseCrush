// Helper function to format time ago
function formatTimeAgo(timestamp) {
    // Handle invalid or missing timestamp
    if (!timestamp) {
        return "Just now";
    }

    try {
        const now = new Date();
        const date = new Date(timestamp); // Parse ISO string from Django

        // Check if date is valid
        if (isNaN(date.getTime())) {
            console.log("Invalid date from timestamp:", timestamp);
            return "Just now";
        }

        const secondsAgo = Math.floor((now - date) / 1000);

        // Less than a minute
        if (secondsAgo < 60) {
            return "Just now";
        }

        // Less than an hour
        if (secondsAgo < 3600) {
            const minutes = Math.floor(secondsAgo / 60);
            return `${minutes} ${minutes === 1 ? 'minute' : 'minutes'} ago`;
        }

        // Less than a day
        if (secondsAgo < 86400) {
            const hours = Math.floor(secondsAgo / 3600);
            return `${hours} ${hours === 1 ? 'hour' : 'hours'} ago`;
        }

        // Less than a week
        if (secondsAgo < 604800) {
            const days = Math.floor(secondsAgo / 86400);
            return `${days} ${days === 1 ? 'day' : 'days'} ago`;
        }

        // Less than a month (approximately)
        if (secondsAgo < 2592000) {
            const weeks = Math.floor(secondsAgo / 604800);
            return `${weeks} ${weeks === 1 ? 'week' : 'weeks'} ago`;
        }

        // Format as date for older items
        const day = String(date.getDate()).padStart(2, '0');
        const month = date.toLocaleString('en-US', { month: 'long' });
        const year = String(date.getFullYear()).slice(-2);

        return `${day} ${month} ${year}`;
    } catch (error) {
        console.error("Error formatting time:", error, "for timestamp:", timestamp);
        return "Just now";
    }
}

// fill profile details
async function fillProfile(userData) {
    // update user profile details
    const username = document.getElementById('username');
    const fullname = document.getElementById('fullname');
    const role = document.getElementById('role');
    const photo = document.getElementById('photo');
    const status = document.getElementById('status');
    username.textContent = `@${userData.username}`;
    fullname.textContent = `${userData.full_name}`;
    role.textContent = `${userData.role.charAt(0).toUpperCase() + userData.role.slice(1).toLowerCase()}`;
    photo.src = userData.photo;
    status.textContent = `${userData.status}`;
}

// get user data
async function getUserData(userId = null) {
    const url = userId ? `/api/user_details_id/${userId}/` : `/api/user_details`;
    const userDataResponse = await fetch(url);
    const userData = await userDataResponse.json();
    return userData;
}

// get users
async function getUsers() {
    const usersResponse = await fetch('/api/users');
    const users = await usersResponse.json();
    return users;
}

// get courses
async function getCourses() {
    // fetch list of courses
    const coursesResponse = await fetch('/api/courses');
    const courses = await coursesResponse.json();
    return courses;
}

// get course
async function getCourse(courseId) {
    const courseResponse = await fetch(`/api/course/${courseId}`);
    const course = await courseResponse.json();
    return course
}

// get notifications
async function getNotifications() {
    const notificationsResponse = await fetch('/api/notifications/');
    const notifications = await notificationsResponse.json();
    return notifications;
}


// get all course material
async function getMaterials() {
    const materialsResponse = await fetch('/api/materials/')
    const materials = await materialsResponse.json();
    return materials;
}


// get all enrolments
async function getEnrolments() {
    const enrolmentsResponse = await fetch('/api/enrolments');
    const enrolments = await enrolmentsResponse.json();
    return enrolments;
}


// get feedbacks
async function getFeedbacks() {
    const feedbacksResponse = await fetch('/api/feedbacks/');
    const feedbacks = await feedbacksResponse.json();
    return feedbacks;
} 