function loadSearchData() {
     let data = document.getElementsByName("summary");
     for (const item of data) {
        item.innerHTML = item.textContent
     }
 }