/**
 * 주변 실거래가 실시간 조회 (국토부 아파트 실거래 API)
 * detail.html의 #price-loading / #price-table 섹션을 채웁니다.
 */
(function () {
  var priceSection = document.getElementById('price-loading');
  if (!priceSection) return;

  var lawdCd  = document.body.dataset.lawdCd  || '';
  var minPrice = parseInt(document.body.dataset.minPrice || '0', 10);
  var aptName  = document.body.dataset.aptName  || '';

  if (!lawdCd) {
    priceSection.innerHTML = '<span style="color:var(--text-muted); font-size:.85rem;">이 지역의 실거래가 정보를 준비 중입니다.</span>';
    return;
  }

  var today = new Date();
  var months = [];
  for (var i = 0; i < 6; i++) {
    var d = new Date(today.getFullYear(), today.getMonth() - i, 1);
    months.push('' + d.getFullYear() + String(d.getMonth() + 1).padStart(2, '0'));
  }

  var API_KEY = document.body.dataset.molandKey || '';
  var base = 'https://apis.data.go.kr/1613000/RTMSDataSvcAptTrade/getRTMSDataSvcAptTrade';

  var allRows = [];
  var pending = months.length;

  function done() {
    pending--;
    if (pending > 0) return;
    render(allRows);
  }

  function fetchMonth(ym) {
    var url = base + '?LAWD_CD=' + lawdCd + '&DEAL_YMD=' + ym
            + '&numOfRows=50&pageNo=1&_type=json&serviceKey=' + encodeURIComponent(API_KEY);
    fetch(url)
      .then(function (r) { return r.json(); })
      .then(function (data) {
        var items = (data.response && data.response.body && data.response.body.items &&
                     data.response.body.items.item) || [];
        if (!Array.isArray(items)) items = [items];
        items.forEach(function (it) {
          allRows.push({
            name:  (it.aptNm || '').trim(),
            type:  it.excluUseAr || '-',
            price: parseInt((it.dealAmount || '0').replace(/,/g, ''), 10),
            ym:    ym.slice(0, 4) + '.' + ym.slice(4, 6),
          });
        });
        done();
      })
      .catch(function () { done(); });
  }

  months.forEach(fetchMonth);

  function render(rows) {
    var loading = document.getElementById('price-loading');
    var table   = document.getElementById('price-table');
    var tbody   = document.getElementById('price-tbody');
    var compare = document.getElementById('price-compare');
    if (!tbody) return;

    rows.sort(function (a, b) { return b.price - a.price; });
    var top = rows.slice(0, 20);

    if (!top.length) {
      loading.innerHTML = '<span style="color:var(--text-muted); font-size:.85rem;">최근 6개월 인근 실거래 데이터가 없습니다.</span>';
      return;
    }

    top.forEach(function (r) {
      var tr = document.createElement('tr');
      var uk = Math.floor(r.price / 10000);
      var man = r.price % 10000;
      var priceStr = uk ? uk + '억' + (man ? ' ' + man.toLocaleString() + '만' : '') : r.price.toLocaleString() + '만';
      tr.innerHTML = '<td>' + esc(r.name) + '</td>'
                   + '<td>' + esc(r.type) + '㎡</td>'
                   + '<td class="num">' + priceStr + '</td>'
                   + '<td>' + esc(r.ym) + '</td>';
      tbody.appendChild(tr);
    });

    loading.style.display = 'none';
    table.style.display   = '';

    // 분양가 vs 실거래가 비교
    if (minPrice && compare) {
      var avgPrice = Math.round(rows.reduce(function (s, r) { return s + r.price; }, 0) / rows.length);
      var diff = minPrice - avgPrice;
      var diffStr = Math.abs(diff).toLocaleString() + '만';
      var arrow = diff > 0 ? '▲' : '▼';
      var cls   = diff > 0 ? 'comp-hot' : 'comp-good';
      var uk2 = Math.floor(minPrice / 10000), man2 = minPrice % 10000;
      var salesStr = uk2 ? uk2 + '억' + (man2 ? ' ' + man2.toLocaleString() + '만' : '') : minPrice.toLocaleString() + '만';
      compare.innerHTML = '<strong>분양가 (최저)</strong> ' + salesStr
        + ' &nbsp;<span class="arrow">' + arrow + '</span>&nbsp;'
        + '주변 평균 실거래가 대비 <span class="' + cls + '">' + diffStr + ' ' + (diff > 0 ? '높음' : '낮음') + '</span>';
    }
  }

  function esc(s) {
    return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  }
})();
