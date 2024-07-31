document.addEventListener('DOMContentLoaded', (event) => {
        const rubric = document.getElementById('rubric');
        const checkboxesPrediction = document.querySelectorAll('.filter-prediction');
        const checkboxesResult = document.querySelectorAll('.filter-result');
        const radiosShow = document.querySelectorAll('input[name="show"]');
        const inputSearch = document.getElementById('filter-search');
        const tableHeaders = document.querySelectorAll('th[data-sort-key]');
        const tbody = document.querySelector('table#constituencies > tbody');
        const tableRows = tbody.querySelectorAll('tr');
        const matrixCells = document.querySelectorAll('#matrix td');

        const sortState = {
                'key': null,
                'model': null,
                'ascending': false,
        }

        function loadState() {
                const url = new URL(window.location);

                if (url.searchParams.get('prediction')) {
                        const params = url.searchParams.get('prediction').split(',');
                        for (let i = 0; i < parties.length; i++) {
                                if (params.includes(parties[i])) {
                                        checkboxesPrediction[i].checked = true;
                                }
                        }
                }

                if (url.searchParams.get('result')) {
                        const params = url.searchParams.get('result').split(',');
                        for (let i = 0; i < parties.length; i++) {
                                if (params.includes(parties[i])) {
                                        checkboxesResult[i].checked = true;
                                }
                        }
                }

                if (url.searchParams.get('show')) {
                        const show = url.searchParams.get('show');
                        if (show) {
                                document.querySelector(`input[name="show"][value="${show}"]`).checked = true;
                        } else {
                                document.querySelector('input[name="show"][value="all"]').checked = true;
                        }
                }

                if (url.searchParams.get('search')) {
                        inputSearch.value = url.searchParams.get('search');
                }
        }

        function filter() {
                let state = {
                        'prediction': [],
                        'result': [],
                        'show': document.querySelector('input[name="show"]:checked').value,
                        'search': inputSearch.value.toLowerCase(),
                };
                for (let i = 0; i < parties.length; i++) {
                        if (checkboxesPrediction[i].checked) {
                                state['prediction'].push(parties[i]);
                        }
                        if (checkboxesResult[i].checked) {
                                state['result'].push(parties[i]);
                        }
                }

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

                if (state['prediction'].length > 0) {
                        newUrl.searchParams.set('prediction', state['prediction'].join(','));
                } else {
                        newUrl.searchParams.delete('prediction');
                }

                if (state['result'].length > 0) {
                        newUrl.searchParams.set('result', state['result'].join(','));
                } else {
                        newUrl.searchParams.delete('result');
                }

                if (state['show'] == 'all') {
                        newUrl.searchParams.delete('show');
                } else {
                        newUrl.searchParams.set('show', state['show']);
                }

                if (state['search'] == '') {
                        newUrl.searchParams.delete('search');
                        if (newUrl.toString() != window.location) {
                                window.history.replaceState({}, '', newUrl);
                        }
                } else if (state['search'] != (newUrl.searchParams.get('search') | '')) {
                        newUrl.searchParams.set('search', state['search']);
                        window.history.replaceState({}, '', newUrl);
                }

                if (newUrl.toString() != window.location) {
                        window.history.pushState({}, '', newUrl);
                }
        }

        function showRow(ix, code, state) {
                if (state['search'] != '') {
                        if (!code.toLowerCase().includes(state['search']) & !(codeToName[code].toLowerCase().includes(state['search']))) {
                                return false;
                        }
                }

                if (state['prediction'].length > 0) {
                        if (!state['prediction'].includes(predictions['winner'][model][code])) {
                                return false;
                        }
                }

                if (state['result'].length > 0) {
                        if (!state['result'].includes(predictions['winner']['2024'][code])) {
                                return false;
                        }
                }

                if (state['show'] == 'hits') {
                        if (predictions['winner']['2024'][code] != predictions['winner'][model][code]) {
                                return false;
                        }
                } else if (state['show'] == 'misses') {
                        if (predictions['winner']['2024'][code] == predictions['winner'][model][code]) {
                                return false;
                        }
                }

                return true;
        }

        function sort() {
                const key = sortState['key'];
                const model = sortState['model'];
                const ascending = sortState['ascending'];
                const rows = Array.from(tableRows)
                rows.sort((r1, r2)=> {
                        const code1 = r1.dataset['constituency'];
                        const code2 = r2.dataset['constituency'];

                        let v1, v2;
                        if (key == 'name') {
                                v1 = codeToName[code1];
                                v2 = codeToName[code2];
                        } else {
                                v1 = predictions[key][model][code1];
                                v2 = predictions[key][model][code2];
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

        function handleTableHeaderClick(e) {
                const th = e.target;
                if ((sortState['key'] == th.dataset['sortKey']) && (sortState['model'] == th.dataset['sortModel'])) {
                        sortState['ascending'] = !sortState['ascending'];
                }
                sortState['key'] = th.dataset['sortKey'];
                sortState['model'] = th.dataset['sortModel'];
                sort();
        }

        function handleMatrixCellClick(e) {
                const td = e.target;
                console.log(td.dataset);
                for (let i = 0; i < parties.length; i++) {
                        checkboxesPrediction[i].checked = (td.dataset['predicted'] == parties[i]);
                        checkboxesResult[i].checked = (td.dataset['result'] == parties[i]);
                }
                filter();
        }

        checkboxesPrediction.forEach(cb => {
                cb.addEventListener('change', filter);
        });
        checkboxesResult.forEach(cb => {
                cb.addEventListener('change', filter);
        });
        radiosShow.forEach(r => {
                r.addEventListener('change', filter);
        });
        inputSearch.addEventListener('keyup', filter);
        tableHeaders.forEach(th => {
                th.addEventListener('click', handleTableHeaderClick);
        })
        matrixCells.forEach(td => {
                td.addEventListener('click', handleMatrixCellClick);
        })

        loadState();
        filter();
});
