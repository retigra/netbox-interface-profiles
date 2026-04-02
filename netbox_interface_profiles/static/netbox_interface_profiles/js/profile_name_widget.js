(function () {
    "use strict";

    /**
     * Convert a string into a URL-safe slug.
     * Strips accents, lowercases, replaces whitespace with hyphens,
     * and removes all characters that are not alphanumeric or hyphens.
     *
     * @param {string} text
     * @returns {string}
     */
    function slugify(text) {
        return text
            .toString()
            .toLowerCase()
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")  // strip diacritic accents
            .replace(/[^a-z0-9\s-]/g, "")     // remove non-alphanumeric (keep spaces and hyphens)
            .trim()
            .replace(/[\s_]+/g, "-")           // collapse whitespace / underscores to a single hyphen
            .replace(/-+/g, "-");              // collapse consecutive hyphens
    }

    /**
     * Return the visible label of the currently selected option in a <select>
     * element, or an empty string if nothing is selected.
     *
     * DynamicModelChoiceField renders as a Select2-enhanced <select>. After
     * the user picks a value, Select2 keeps the selected <option> in the DOM,
     * so reading options[selectedIndex].text is reliable.
     *
     * @param {string} selectId  The id attribute of the <select> element.
     * @returns {string}
     */
    function getSelectedLabel(selectId) {
        const el = document.getElementById(selectId);
        if (!el) return "";
        const opt = el.options[el.selectedIndex];
        return opt && opt.value ? opt.text.trim() : "";
    }

    /**
     * Build the profile name slug from the current scope field values.
     * Format: {platform}-{device_type}-{interface_profile}
     * device_type is omitted when no value is selected.
     *
     * @returns {string}
     */
    function buildName() {
        const platform = getSelectedLabel("id_platform");
        const deviceType = getSelectedLabel("id_device_type");
        const interfaceProfile = getSelectedLabel("id_interface_profile");

        return [platform, deviceType, interfaceProfile]
            .filter(Boolean)
            .map(slugify)
            .join("-");
    }

    document.addEventListener("DOMContentLoaded", function () {
        const btn = document.getElementById("btn-generate-profile-name");
        if (!btn) return;

        btn.addEventListener("click", function () {
            const nameField = document.getElementById("id_name");
            if (nameField) {
                nameField.value = buildName();
            }
        });
    });
})();
