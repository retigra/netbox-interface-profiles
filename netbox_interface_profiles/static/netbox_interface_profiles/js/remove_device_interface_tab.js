(function () {
    "use strict";

    /**
     * Return true when href points to /dcim/devices/{id}/interfaces/.
     *
     * @param {string} href
     * @returns {boolean}
     */
    function isDeviceInterfacesHref(href) {
        if (!href) return false;

        const url = new URL(href, window.location.origin);
        return /^\/dcim\/devices\/\d+\/interfaces\/?$/.test(url.pathname);
    }

    /**
     * Remove any presentation nav-item whose link targets the device
     * interfaces route.
     */
    function removeDeviceInterfacesTab() {
        const navItems = document.querySelectorAll(
            'li.nav-item[role="presentation"]',
        );

        navItems.forEach((item) => {
            const hasMatchingLink = Array.from(item.querySelectorAll("a[href]"))
                .some((link) =>
                    isDeviceInterfacesHref(link.getAttribute("href"))
                );

            if (hasMatchingLink) {
                item.remove();
            }
        });
    }

    document.addEventListener("DOMContentLoaded", removeDeviceInterfacesTab);
})();
