(function () {
    "use strict";

    const DEVICE_INTERFACES_PATH = /^(\/dcim\/devices\/\d+\/)interfaces\/?$/;

    /**
     * Return true when href points to /dcim/devices/{id}/interfaces/.
     *
     * @param {string} href
     * @returns {boolean}
     */
    function isDeviceInterfacesHref(href) {
        if (!href) return false;

        const url = new URL(href, window.location.origin);
        return DEVICE_INTERFACES_PATH.test(url.pathname);
    }

    /**
     * Map /dcim/devices/{id}/interfaces/ to /dcim/devices/{id}/interface-profiles/,
     * or return null when path is not the device interfaces route.
     *
     * @param {string} path
     * @returns {string|null}
     */
    function toInterfaceProfilesPath(path) {
        const match = DEVICE_INTERFACES_PATH.exec(path);
        return match ? `${match[1]}interface-profiles/` : null;
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

    /**
     * Point links to the device interfaces route, and return_url parameters
     * targeting it, to the interface profiles tab instead. Covers links
     * rendered by NetBox core, such as the interface breadcrumb and the
     * "Add Components" menu. Links marked data-legacy-interfaces are kept.
     */
    function redirectDeviceInterfacesLinks() {
        // Leave the legacy view intact when the user deliberately opened it
        if (isDeviceInterfacesHref(window.location.href)) return;

        document.querySelectorAll("a[href]").forEach((link) => {
            if (link.hasAttribute("data-legacy-interfaces")) return;

            const url = new URL(link.getAttribute("href"), window.location.origin);
            if (url.origin !== window.location.origin) return;

            let changed = false;

            const path = toInterfaceProfilesPath(url.pathname);
            if (path) {
                url.pathname = path;
                changed = true;
            }

            const returnUrl = url.searchParams.get("return_url");
            if (returnUrl) {
                const returnTo = new URL(returnUrl, window.location.origin);
                const returnPath = toInterfaceProfilesPath(returnTo.pathname);
                if (returnPath) {
                    url.searchParams.set("return_url", returnPath + returnTo.search);
                    changed = true;
                }
            }

            if (changed) {
                link.setAttribute("href", url.pathname + url.search + url.hash);
            }
        });
    }

    document.addEventListener("DOMContentLoaded", () => {
        removeDeviceInterfacesTab();
        redirectDeviceInterfacesLinks();
    });
})();
