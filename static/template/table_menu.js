// sidebar collaps 
document.addEventListener('DOMContentLoaded', function () {
    const categoryLinks = document.querySelectorAll('.category-link');

    categoryLinks.forEach(link => {
        link.addEventListener('click', function () {
            const category = this.dataset.category;
            const subcategoryList = document.getElementById(`subcats-${category}`);

            // Collapse all other subcategories before opening the clicked one
            document.querySelectorAll('.subcategory-list').forEach(list => {
                if (list !== subcategoryList) {
                    list.style.maxHeight = '0';
                    list.classList.remove('active');
                }
            });

            // Toggle the clicked subcategory
            if (subcategoryList.classList.contains('active')) {
                subcategoryList.style.maxHeight = '0';
                subcategoryList.classList.remove('active');
            } else {
                subcategoryList.style.maxHeight = subcategoryList.scrollHeight + 'px';
                subcategoryList.classList.add('active');
            }
        });
    });
});


// show product in main content 
document.querySelectorAll('.subcategory-link').forEach(link => {
    link.addEventListener('click', function() {
        // Get the subcategory from the clicked link
        const selectedSubcategory = this.getAttribute('data-subcategory');
        
        // Hide all categories initially
        document.querySelectorAll('.category').forEach(category => {
            category.style.display = 'none';
        });

        // Show the products in the selected subcategory
        document.querySelectorAll('.category[data-subcategory="' + selectedSubcategory + '"]').forEach(category => {
            category.style.display = 'block';
            category.querySelectorAll('.product-card1').forEach(productCard => {
                productCard.style.display = 'block'; // Show products
            });
        });
    });
});



document.addEventListener('DOMContentLoaded', function() {
    const searchBtn = document.getElementById('search-btn');
    const searchInput = document.getElementById('search-input');
    const noResultsMessage = document.getElementById('no-results-message'); // Element for displaying no results message

    // Search function to filter products and subproducts
    function searchProducts() {
        const searchTerm = searchInput.value.trim().toLowerCase();
        console.log("Search term: ", searchTerm);  // Debugging line to check the search term

        const categories = document.querySelectorAll('.category');
        let anyProductMatched = false; // Flag to track if any product is matched

        categories.forEach(category => {
            const subcategory = category.getAttribute('data-subcategory').toLowerCase();
            const products = category.querySelectorAll('.menu-items .menu-item');

            let subcategoryMatch = false;
            products.forEach(product => {
                const productName = product.textContent.toLowerCase();
                if (productName.includes(searchTerm)) {
                    product.style.display = 'block';
                    subcategoryMatch = true;
                    anyProductMatched = true; // At least one product matched
                } else {
                    product.style.display = 'none';
                }
            });

            // Show or hide the subcategory based on product matches
            if (subcategory.includes(searchTerm) || subcategoryMatch) {
                category.style.display = 'block';
            } else {
                category.style.display = 'none';
            }
        });

        // Show or hide no results message
        if (anyProductMatched) {
            noResultsMessage.style.display = 'none'; // Hide message if products matched
        } else {
            noResultsMessage.style.display = 'block'; // Show message if no products matched
        }
    }

    // Function to handle clicking on a product to show the price
    function showProductPrice(event) {
        const productId = event.currentTarget.getAttribute('data-id');
        const priceElement = document.getElementById('pricepr' + productId);

        // Toggle price visibility
        if (priceElement.style.display === 'none') {
            priceElement.style.display = 'block';
        } else {
            priceElement.style.display = 'none';
        }
    }

    // Attach event to search button
    searchBtn.addEventListener('click', searchProducts);

    // Trigger search on Enter key
    searchInput.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            searchProducts();
        }
    });

    // Attach click event to all product buttons to show price on click
    document.querySelectorAll('.product-button').forEach(button => {
        button.addEventListener('click', showProductPrice);
    });
});
