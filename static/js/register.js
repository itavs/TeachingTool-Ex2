"use strict";
// GET only renders the form. Registration is always a CSRF-protected POST.
const registration = document.getElementById("attendance-registration");
if (registration) {
    document.getElementById("registration-progress").textContent = "Submitting attendance…";
    registration.requestSubmit();
}
