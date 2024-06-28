console.log("hello");
document.addEventListener('DOMContentLoaded', (event) => {
        const parties = ["con", "grn", "lab", "lib", "oth", "pc", "snp", "ref"];
        const inputSearch = document.getElementById('filter-search');
        const checkboxes2019 = document.querySelectorAll('.filter-2019');
        const checkboxes2024 = document.querySelectorAll('.filter-2024');
        const radiosPredictionType = document.querySelectorAll('.filter-prediction-type');
        const dropdownItems = document.querySelectorAll('.dropdown-item');
        const tableRows = document.querySelectorAll('table#constituencies > tbody > tr');

        function loadState() {
                const url = new URL(window.location);

                if (url.searchParams.get('search')) {
                        inputSearch.value = url.searchParams.get('search');
                }

                if (url.searchParams.get('2019')) {
                        const params2019 = url.searchParams.get('2019').split(',');
                        for (let i = 0; i < parties.length; i++) {
                                if (params2019.includes(parties[i])) {
                                        checkboxes2019[i].checked = true;
                                }
                        }
                }
                if (url.searchParams.get('2024')) {
                        const params2024 = url.searchParams.get('2024').split(',');
                        for (let i = 0; i < parties.length; i++) {
                                if (params2024.includes(parties[i])) {
                                        checkboxes2024[i].checked = true;
                                }
                        }
                }
                if (url.searchParams.get('prediction-type')) {
                        const predictionType = url.searchParams.get('prediction-type');
                        if (isNaN(parseInt(predictionType))) {
                                document.querySelector(`input[name="prediction-type"][value="${predictionType}"]`).checked = true
                        } else {
                                const radio = document.querySelector('input#prediction-type-at-least');
                                const button = document.querySelector('#prediction-type-at-least-button');
                                radio.checked = true;
                                radio.value = predictionType;
                                button.innerHTML = `At least ${predictionType}`;
                                button.classList.add('btn-secondary');
                                button.classList.remove('btn-outline-secondary');
                        }
                }
        }

        function update() {
                let state = {
                        'search': inputSearch.value.toLowerCase(),
                        '2019': [],
                        '2024': [],
                        'predictionType': document.querySelector('input[name="prediction-type"]:checked').value,
                };
                for (let i = 0; i < parties.length; i++) {
                        if (checkboxes2019[i].checked) {
                                state['2019'].push(parties[i]);
                        }
                        if (checkboxes2024[i].checked) {
                                state['2024'].push(parties[i]);
                        }
                }

                console.log(state);

                tableRows.forEach((tr, ix) => {
                        tr.style.display = showRow(ix, tr, state) ? '' : 'none';
                })

                const nRows = tableRows.length;
                let nRowsShown = 0;
                for (let i = 0; i < tableRows.length; i++) {
                        if (tableRows[i].style.display == '') {
                                nRowsShown++;
                        }
                }

                if (nRowsShown == nRows) {
                        document.getElementById('constituencies-summary').textContent = `all ${nRows} constituencies`;
                } else if (nRowsShown == 1) {
                        document.getElementById('constituencies-summary').textContent = '1 matching constituency';
                } else {
                        document.getElementById('constituencies-summary').textContent = `${nRowsShown} matching constituencies`;
                }

                let newUrl = new URL(window.location);

                if (state['search'] == '') {
                        newUrl.searchParams.delete('search');
                        if (newUrl.toString() != window.location) {
                                window.history.replaceState({}, '', newUrl);
                        }
                } else if (state['search'] != (newUrl.searchParams.get('search') | '')) {
                        newUrl.searchParams.set('search', state['search']);
                        window.history.replaceState({}, '', newUrl);
                }

                if (state['2019'].length > 0) {
                        newUrl.searchParams.set('2019', state['2019'].join(','));
                } else {
                        newUrl.searchParams.delete('2019');
                }
                if (state['2024'].length > 0) {
                        newUrl.searchParams.set('2024', state['2024'].join(','));
                } else {
                        newUrl.searchParams.delete('2024');
                }
                if (state['predictionType'] == 'all') {
                        newUrl.searchParams.delete('prediction-type');
                } else {
                        newUrl.searchParams.set('prediction-type', state['predictionType']);
                }
                if (newUrl.toString() != window.location) {
                        window.history.pushState({}, '', newUrl);
                }
        }

        function handlePredictionTypeRadioClick(e) {
                const button = document.querySelector('#prediction-type-at-least-button');
                button.innerHTML = 'At least...';
                button.classList.add('btn-outline-secondary');
                button.classList.remove('btn-secondary');
                update();
        }

        function handlePredictionTypeDropdownItemClick(e) {
                const radio = document.querySelector('input#prediction-type-at-least');
                const button = document.querySelector('#prediction-type-at-least-button');
                radio.checked = true;
                radio.value = e.target.text;
                button.innerHTML = `At least ${e.target.text}`;
                button.classList.add('btn-secondary');
                button.classList.remove('btn-outline-secondary');
                update();
        }

        function showRow(ix, tr, state) {
                const dataset = tr.dataset;
                const parties2019 = new Set(state['2019']);
                const parties2024 = new Set(state['2024']);

                if (ix < 5) {
                        console.log(dataset);
                }

                if (state['search'] != '') {
                        const code = tr.getElementsByTagName('td')[0].textContent.toLowerCase();
                        const name = tr.getElementsByTagName('td')[1].textContent.toLowerCase();
                        if (!code.includes(state['search']) & !(name.includes(state['search']))) {
                                return false;
                        }
                }

                if (parties2019.size > 0) {
                        if (!parties2019.has(dataset['2019'])) {
                                return false;
                        }
                }
                if (parties2024.size > 0) {
                        if (state['predictionType'] == 'all') {
                                const dataset2024 = new Set(dataset['2024'].split(','));
                                if (!setEq(parties2024, dataset2024)) {
                                        return false;
                                }
                        } else if (state['predictionType'] == 'any') {
                                const dataset2024 = new Set(dataset['2024'].split(','));
                                if (!isSubset(parties2024, dataset2024)) {
                                        return false;
                                }
                        } else if (state['predictionType'] == 'none') {
                                const dataset2024 = new Set(dataset['2024'].split(','));
                                if (setInt(parties2024, dataset2024).size > 0) {
                                        return false;
                                }
                        } else {
                                const dataset2024 = dataset['2024'].split(',');
                                const minCount = parseInt(state['predictionType'], 10);
                                for (p of parties2024) {
                                        let c = 0;
                                        for (p1 of dataset2024) {
                                                if (p == p1) {
                                                        c += 1;
                                                }
                                        }
                                        if (c < minCount) {
                                                return false
                                        }
                                }
                        }
                }
                return true;
        }

        const setEq = (xs, ys) => xs.size === ys.size && [...xs].every((x) => ys.has(x));
        const setInt = (xs, ys) => new Set([...xs].filter(x => ys.has(x)));
        const isSubset = (xs, ys) => Array.from(xs).every(x => ys.has(x));

        inputSearch.addEventListener('keyup', update);
        checkboxes2019.forEach(cb => {
                cb.addEventListener('change', update);
        });
        checkboxes2024.forEach(cb => {
                cb.addEventListener('change', update);
        });
        radiosPredictionType.forEach(r => {
                r.addEventListener('change', handlePredictionTypeRadioClick);
        });
        dropdownItems.forEach(i => {
                i.addEventListener('click', handlePredictionTypeDropdownItemClick);
        });
        
        loadState();
        update();
});

