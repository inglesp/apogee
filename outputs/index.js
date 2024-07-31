document.addEventListener('DOMContentLoaded', (event) => {
	const predictiveModels = models.slice(2);  // excluding 2019 + 2024

        const rubric = document.getElementById('rubric');
        const radiosShow = document.querySelectorAll('input[name="show"]');
        const radiosShowParty = document.querySelectorAll('input[name="show-party"]');
        const checkboxes2019 = document.querySelectorAll('.filter-2019');
        const checkboxes2024Result = document.querySelectorAll('.filter-2024-result');
        const radios2024ResultDeclared = document.querySelectorAll('input[name="2024-result-declared"]');
        const checkboxes2024 = document.querySelectorAll('.filter-2024');
        const radiosPredictionType = document.querySelectorAll('input[name="prediction-type"]');
        const inputSearch = document.getElementById('filter-search');
        const dropdownItems = document.querySelectorAll('.dropdown-item');
        const tableHeaders = document.querySelectorAll('table#constituencies th:nth-child(n+2)');
        const tbody = document.querySelector('table#constituencies > tbody');
        const tableRows = tbody.querySelectorAll('tr');

	const sortState = {
		'key': null,
		'heading': null,
		'ascending': false,
	}

        function loadState() {
                const url = new URL(window.location);

                if (url.searchParams.get('show')) {
                        const show = url.searchParams.get('show');
                        if (show.startsWith('vote-share')) {
                                document.querySelector('input[name="show"][value="vote-share"]').checked = true;
                        } else if (show.startsWith('majority')) {
                                document.querySelector('input[name="show"][value="majority"]').checked = true;
                        }
                        const party = show.split('-').slice(-1)[0];
                        document.querySelector(`input[name="show-party"][value="${party}"]`).checked = true;
                }

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
                if (url.searchParams.get('2024-result')) {
                        const params2024Result = url.searchParams.get('2024-result').split(',');
                        for (let i = 0; i < parties.length; i++) {
                                if (params2024Result.includes(parties[i])) {
                                        checkboxes2024Result[i].checked = true;
                                }
                        }
                }
                if (url.searchParams.get('2024-result-declared')) {
                        const params2024ResultDeclared = url.searchParams.get('2024-result-declared');
			document.querySelector(`input[name="2024-result-declared"][value="${params2024ResultDeclared}"]`).checked = true;
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
                                document.querySelector(`input[name="prediction-type"][value="${predictionType}"]`).checked = true;
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

        function updateValues() {
                const show = document.querySelector('input[name="show"]:checked').value;
                let key;
                if (show == 'winner') {
                        key = 'winner'
                        document.getElementById('show-parties').classList.add('d-none');
                        rubric.querySelector('#show').textContent = 'winner';
                } else {
                        const party = document.querySelector('input[name="show-party"]:checked').value;
                        key = `${show}-${party}`
                        document.getElementById('show-parties').classList.remove('d-none');
                        if (show == 'vote-share') {
                               rubric.querySelector('#show').textContent = `${party} vote share`;
                        } else {
                                rubric.querySelector('#show').textContent = `${party} majority`;
                        }
                }

                tableRows.forEach(tr => {
                        const code = tr.dataset['constituency'];
                        const tds = tr.querySelectorAll('td');
                        models.forEach((m, ix) => {
                                const td = tds[ix + 2];
                                if (show == 'winner') {
                                        td.textContent = predictions[key][m][code];
                                } else {
                                        td.textContent = `${predictions[key][m][code]}%`;
                                }
                        })
                })

                tableHeaders.forEach(th1 => {
                        th1.classList.remove('table-active');
                        delete th1.dataset['sorted'];
                });

                let newUrl = new URL(window.location);
                if (key == 'winner') {
                        newUrl.searchParams.delete('show');
                } else {
                        newUrl.searchParams.set('show', key);
                }
                if (newUrl.toString() != window.location) {
                        window.history.pushState({}, '', newUrl);
                }
        }

        function filter() {
                let state = {
                        'search': inputSearch.value.toLowerCase(),
                        '2019': [],
                        '2024-result': [],
                        '2024-result-declared': document.querySelector('input[name="2024-result-declared"]:checked').value,
                        '2024': [],
                        'prediction-type': document.querySelector('input[name="prediction-type"]:checked').value,
                };
                for (let i = 0; i < parties.length; i++) {
                        if (checkboxes2019[i].checked) {
                                state['2019'].push(parties[i]);
                        }
                        if (checkboxes2024Result[i].checked) {
                                state['2024-result'].push(parties[i]);
                        }
                        if (checkboxes2024[i].checked) {
                                state['2024'].push(parties[i]);
                        }
                }

                console.log(state);

                tableRows.forEach((tr, ix) => {
                        tr.style.display = showRow(ix, tr.dataset['constituency'], state) ? '' : 'none';
                })

                const nRows = tableRows.length;
                let nRowsShown = 0;
                for (let i = 0; i < tableRows.length; i++) {
                        if (tableRows[i].style.display == '') {
                                nRowsShown++;
                        }
                }

                if (nRowsShown == nRows) {
                        rubric.querySelector('#count').textContent = `all ${nRows} constituencies`;
                } else if (nRowsShown == 1) {
                        rubric.querySelector('#count').textContent = '1 matching constituency';
                } else {
                        rubric.querySelector('#count').textContent = `${nRowsShown} matching constituencies`;
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
                if (state['2024-result'].length > 0) {
                        newUrl.searchParams.set('2024-result', state['2024-result'].join(','));
                } else {
                        newUrl.searchParams.delete('2024-result');
                }
                if (state['2024-result-declared'] == 'all') {
                        newUrl.searchParams.delete('2024-result-declared');
                } else {
                        newUrl.searchParams.set('2024-result-declared', state['2024-result-declared']);
                }
                if (state['2024'].length > 0) {
                        newUrl.searchParams.set('2024', state['2024'].join(','));
                } else {
                        newUrl.searchParams.delete('2024');
                }
                if (state['prediction-type'] == 'all') {
                        newUrl.searchParams.delete('prediction-type');
                } else {
                        newUrl.searchParams.set('prediction-type', state['prediction-type']);
                }
                if (newUrl.toString() != window.location) {
                        window.history.pushState({}, '', newUrl);
                }
        }

        function showRow(ix, code, state) {
                const filter2019 = new Set(state['2019']);
                const filter2024Result = new Set(state['2024-result']);
                const filter2024 = new Set(state['2024']);

                if (state['search'] != '') {
                        if (!code.toLowerCase().includes(state['search']) & !(codeToName[code].toLowerCase().includes(state['search']))) {
                                return false;
                        }
                }

                if (filter2019.size > 0) {
                        if (!filter2019.has(predictions['winner']['2019'][code])) {
				return false;
			}
                }

                if (filter2024Result.size > 0) {
                        if (!filter2024Result.has(predictions['winner']['2024'][code])) {
				return false;
			}
                }

		if (state['2024-result-declared'] == 'declared') {
			if (predictions['winner']['2024'][code] == '?') {
				return false;
			}
		} else if (state['2024-result-declared'] == 'undeclared') {
			if (predictions['winner']['2024'][code] != '?') {
				return false;
			}
		}

                if (filter2024.size > 0) {
                        if (state['prediction-type'] == 'all') {
                                const predictions2024 = new Set(predictiveModels.map(m => predictions['winner'][m][code]));
                                if (!setEq(filter2024, predictions2024)) {
                                        return false;
                                }
                        } else if (state['prediction-type'] == 'any') {
                                const predictions2024 = new Set(predictiveModels.map(m => predictions['winner'][m][code]));
                                if (!isSubset(filter2024, predictions2024)) {
                                        return false;
                                }
                        } else if (state['prediction-type'] == 'none') {
                                const predictions2024 = new Set(predictiveModels.map(m => predictions['winner'][m][code]));
                                if (setInt(filter2024, predictions2024).size > 0) {
                                        return false;
                                }
                        } else {
                                const predictions2024 = predictiveModels.map(m => predictions['winner'][m][code]);
                                const minCount = parseInt(state['prediction-type'], 10);
                                for (p of filter2024) {
                                        let c = 0;
                                        for (p1 of predictions2024) {
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

        function sort() {
		const heading = sortState['heading'];
		const key = sortState['key'];
		const ascending = sortState['ascending'];
		console.log('sort', heading, key, ascending);
                const rows = Array.from(tableRows)
                rows.sort((r1, r2)=> {
                        const code1 = r1.dataset['constituency'];
                        const code2 = r2.dataset['constituency'];

			let v1, v2;
			if (heading == 'constituency') {
				v1 = codeToName[code1];
				v2 = codeToName[code2];
			} else if (heading == 'avg-error') {
				v1 = avgError[code1];
				v2 = avgError[code2];
			} else if (heading == 'num-correct') {
				v1 = numCorrect[code1];
				v2 = numCorrect[code2];
			} else {
				v1 = predictions[key][heading][code1];
				v2 = predictions[key][heading][code2];
			}

			if (v1 == '?') {
				v1 = -1;
			}
			if (v2 == '?') {
				v2 = -1;
			}

			let rv = 0;
                        if (v1 < v2) {
                                rv = ascending ? -1 : 1;
                        } else if (v2 < v1) {
                                rv = ascending ? 1 : -1;
                        }

			return rv;
                });

                rows.forEach(r => tbody.appendChild(r));
        }

        function handlePredictionTypeRadioClick(e) {
                const button = document.querySelector('#prediction-type-at-least-button');
                button.innerHTML = 'At least...';
                button.classList.add('btn-outline-secondary');
                button.classList.remove('btn-secondary');
                filter();
        }

        function handlePredictionTypeDropdownItemClick(e) {
                const radio = document.querySelector('input#prediction-type-at-least');
                const button = document.querySelector('#prediction-type-at-least-button');
                radio.checked = true;
                radio.value = e.target.text;
                button.innerHTML = `At least ${e.target.text}`;
                button.classList.add('btn-secondary');
                button.classList.remove('btn-outline-secondary');
                filter();
        }

        function handleTableHeaderClick(e) {
                const th = e.target;
		th.classList.add('table-active');
                tableHeaders.forEach(th1 => {
                        if (th1 != th) {
                                th1.classList.remove('table-active');
                        }
                });
		sortState['key'] = new URL(window.location).searchParams.get('show') || 'winner';
		if (sortState['heading'] == th.dataset['heading']) {
			sortState['ascending'] = !sortState['ascending'];
		}
		sortState['heading'] = th.dataset['heading'];
                sort();
        }

        const setEq = (xs, ys) => xs.size === ys.size && [...xs].every((x) => ys.has(x));
        const setInt = (xs, ys) => new Set([...xs].filter(x => ys.has(x)));
        const isSubset = (xs, ys) => Array.from(xs).every(x => ys.has(x));

        radiosShow.forEach(r => {
                r.addEventListener('change', updateValues);
        });
        radiosShowParty.forEach(r => {
                r.addEventListener('change', updateValues);
        });
        checkboxes2019.forEach(cb => {
                cb.addEventListener('change', filter);
        });
        checkboxes2024Result.forEach(cb => {
                cb.addEventListener('change', filter);
        });
        radios2024ResultDeclared.forEach(r => {
                r.addEventListener('change', filter);
        });
        checkboxes2024.forEach(cb => {
                cb.addEventListener('change', filter);
        });
        radiosPredictionType.forEach(r => {
                r.addEventListener('change', handlePredictionTypeRadioClick);
        });
        dropdownItems.forEach(i => {
                i.addEventListener('click', handlePredictionTypeDropdownItemClick);
        });
        inputSearch.addEventListener('keyup', filter);
        tableHeaders.forEach(th => {
                th.addEventListener('click', handleTableHeaderClick);
        })
        
        loadState();
        updateValues();
        filter();
});

