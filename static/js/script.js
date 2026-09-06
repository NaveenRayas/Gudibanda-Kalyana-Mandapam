// ==========================================
// CALENDAR VARIABLES
// ==========================================

const yearSelect = document.getElementById("year");
const monthSelect = document.getElementById("month");
const calendarTitle = document.getElementById("calendar-title");
const calendarDays = document.getElementById("calendar-days");


// ==========================================
// CHECK HTML ELEMENTS
// ==========================================

if (!yearSelect) {
    console.error("ERROR: #year element not found");
}

if (!monthSelect) {
    console.error("ERROR: #month element not found");
}

if (!calendarTitle) {
    console.error("ERROR: #calendar-title element not found");
}

if (!calendarDays) {
    console.error("ERROR: #calendar-days element not found");
}


// ==========================================
// CURRENT CALENDAR
// ==========================================

let currentYear = null;
let currentMonth = null;


// ==========================================
// OFFICIAL TTD WEBSITE
// ==========================================

const officialTTDWebsite =
    "https://tirupatibalaji.ap.gov.in/#/kmCal";


// ==========================================
// SHOW CALENDAR
// ==========================================

function showCalendar() {

    if (!yearSelect || !monthSelect) {
        console.error("Year or Month select element missing");
        return;
    }

    const year = parseInt(yearSelect.value);
    const month = parseInt(monthSelect.value);

    if (isNaN(year) || isNaN(month)) {

        calendarTitle.innerText = "Select Year & Month";

        calendarDays.innerHTML = `
            <div class="calendar-message">
                Please select both year and month.
            </div>
        `;

        return;
    }

    currentYear = year;
    currentMonth = month;

    loadCalendar(year, month);
}


// ==========================================
// LOAD CALENDAR
// ==========================================

function loadCalendar(year, month) {

    const monthNames = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December"
    ];

    calendarTitle.innerText =
        `${monthNames[month]} ${year}`;


    // ==========================================
    // GET AVAILABILITY FROM FLASK
    // ==========================================

    const url =
    `/api/availability?year=${year}&month=${month}`;

    console.log("Fetching:", url);

    fetch(url)

        .then(response => {

            console.log(
                "Response status:",
                response.status
            );

            if (!response.ok) {

                throw new Error(
                    `Server returned ${response.status}`
                );
            }

            return response.json();

        })

        .then(data => {

            console.log("Availability data:", data);

            calendarDays.innerHTML = "";


            // ==========================================
            // FIRST DAY OF MONTH
            // ==========================================

            const firstDay =
                new Date(
                    year,
                    month,
                    1
                ).getDay();


            // ==========================================
            // TOTAL DAYS
            // ==========================================

            const totalDays =
                new Date(
                    year,
                    month + 1,
                    0
                ).getDate();


            // ==========================================
            // TODAY
            // ==========================================

            const today = new Date();

            today.setHours(
                0,
                0,
                0,
                0
            );


            // ==========================================
            // EMPTY DAYS
            // ==========================================

            for (
                let i = 0;
                i < firstDay;
                i++
            ) {

                const emptyDay =
                    document.createElement("div");

                emptyDay.classList.add(
                    "calendar-day",
                    "empty"
                );

                calendarDays.appendChild(
                    emptyDay
                );
            }


            // ==========================================
            // CREATE DAYS
            // ==========================================

            for (
                let day = 1;
                day <= totalDays;
                day++
            ) {

                const dayElement =
                    document.createElement("div");

                dayElement.classList.add(
                    "calendar-day"
                );


                // ==========================================
                // DATE
                // ==========================================

                const date =
                    `${year}-${String(month + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`;


                const selectedDate =
                    new Date(
                        year,
                        month,
                        day
                    );

                selectedDate.setHours(
                    0,
                    0,
                    0,
                    0
                );


                // ==========================================
                // PAST DATE
                // ==========================================

                if (selectedDate < today) {

                    dayElement.classList.add(
                        "past"
                    );

                }


                // ==========================================
                // BOOKED
                // ==========================================

                else if (
                    data.booked &&
                    data.booked.includes(date)
                ) {

                    dayElement.classList.add(
                        "booked"
                    );

                }


                // ==========================================
                // PENDING
                // ==========================================

                else if (
                    data.pending &&
                    data.pending.includes(date)
                ) {

                    dayElement.classList.add(
                        "pending"
                    );

                }


                // ==========================================
                // BLOCKED
                // ==========================================

                else if (
                    data.blocked &&
                    data.blocked.includes(date)
                ) {

                    dayElement.classList.add(
                        "blocked"
                    );

                }


                // ==========================================
                // AVAILABLE
                // ==========================================

                else {

                    dayElement.classList.add(
                        "available"
                    );

                }


                // ==========================================
                // DISPLAY DAY
                // ==========================================

                dayElement.innerText = day;


                // ==========================================
                // AVAILABLE DATE CLICK
                // ==========================================

                if (
                    dayElement.classList.contains(
                        "available"
                    )
                ) {

                    dayElement.style.cursor =
                        "pointer";

                    dayElement.title =
                        "Click to book on official TTD website";


                    dayElement.onclick =
                        function () {

                            const confirmBooking =
                                window.confirm(
                                    `You selected ${date}.\n\n` +
                                    `To book this date, you will be redirected to the official TTD website.\n\n` +
                                    `Continue?`
                                );


                            if (confirmBooking) {

                                window.open(
                                    officialTTDWebsite,
                                    "_blank"
                                );

                            }

                        };

                }


                // ==========================================
                // ADD DAY
                // ==========================================

                calendarDays.appendChild(
                    dayElement
                );

            }

        })

        .catch(error => {

            console.error(
                "Availability error:",
                error
            );

            calendarDays.innerHTML = `
                <div class="calendar-message">
                    Unable to load availability.
                    <br>
                    <small>${error.message}</small>
                </div>
            `;

        });

}


// ==========================================
// PREVIOUS MONTH
// ==========================================

function previousMonth() {

    if (
        currentYear === null ||
        currentMonth === null
    ) {
        return;
    }

    currentMonth--;

    if (currentMonth < 0) {

        currentMonth = 11;
        currentYear--;

    }

    yearSelect.value = currentYear;
    monthSelect.value = currentMonth;

    loadCalendar(
        currentYear,
        currentMonth
    );
}


// ==========================================
// NEXT MONTH
// ==========================================

function nextMonth() {

    if (
        currentYear === null ||
        currentMonth === null
    ) {
        return;
    }

    currentMonth++;

    if (currentMonth > 11) {

        currentMonth = 0;
        currentYear++;

    }

    yearSelect.value = currentYear;
    monthSelect.value = currentMonth;

    loadCalendar(
        currentYear,
        currentMonth
    );
}


// ==========================================
// JAVASCRIPT LOADED
// ==========================================

console.log(
    "Gudibanda Availability Calendar Loaded Successfully"
);