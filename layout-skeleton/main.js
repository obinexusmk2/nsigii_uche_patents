   let isLoading = true;

        const patterns = {
            z: {
                real: `
                    <div class="z-pattern__content with-drop-cap">
                        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.
                    </div>
                    <div class="z-pattern__content with-drop-cap">
                        Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Donec velit neque, auctor sit amet aliquam vel, ullamcorper sit amet ligula.
                    </div>
                `,
                skeleton: `
                    <div class="z-pattern__content">
                        <div class="skeleton-text-group">
                            <div class="skeleton-text"></div>
                            <div class="skeleton-text"></div>
                            <div class="skeleton-text"></div>
                        </div>
                    </div>
                    <div class="z-pattern__content">
                        <div class="skeleton-text-group">
                            <div class="skeleton-text"></div>
                            <div class="skeleton-text"></div>
                            <div class="skeleton-text"></div>
                        </div>
                    </div>
                `
            },
            f: {
                real: `
                    <div class="f-pattern__header with-drop-cap">
                        Welcome to our F-Pattern layout demonstration. This header spans the full width.
                    </div>
                    <div class="f-pattern__section">
                        <div class="f-pattern__content with-drop-cap">
                            Nulla quis lorem ut libero malesuada feugiat. Vestibulum ac diam sit amet quam vehicula elementum sed sit amet dui. Curabitur aliquet quam id dui posuere blandit.
                        </div>
                        <div class="f-pattern__sidebar">
                            Sidebar content with supporting information
                        </div>
                    </div>
                    <div class="f-pattern__section">
                        <div class="f-pattern__content with-drop-cap">
                            Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Donec velit neque, auctor sit amet aliquam vel.
                        </div>
                        <div class="f-pattern__sidebar">
                            Additional sidebar information
                        </div>
                    </div>
                `,
                skeleton: `
                    <div class="f-pattern__header">
                        <div class="skeleton-text-group">
                            <div class="skeleton-text"></div>
                            <div class="skeleton-text"></div>
                        </div>
                    </div>
                    <div class="f-pattern__section">
                        <div class="f-pattern__content">
                            <div class="skeleton-text-group">
                                <div class="skeleton-text"></div>
                                <div class="skeleton-text"></div>
                                <div class="skeleton-text"></div>
                            </div>
                        </div>
                        <div class="f-pattern__sidebar">
                            <div class="skeleton-text"></div>
                        </div>
                    </div>
                    <div class="f-pattern__section">
                        <div class="f-pattern__content">
                            <div class="skeleton-text-group">
                                <div class="skeleton-text"></div>
                                <div class="skeleton-text"></div>
                                <div class="skeleton-text"></div>
                            </div>
                        </div>
                        <div class="f-pattern__sidebar">
                            <div class="skeleton-text"></div>
                        </div>
                    </div>
                `
            },
            t: {
                real: `
                    <div class="t-pattern__header with-drop-cap">
                        T-Pattern Layout Header
                    </div>
                    <div class="t-pattern__content">
                        <div class="t-pattern__section with-drop-cap">
                            Section 1 content in the T-Pattern layout
                        </div>
                        <div class="t-pattern__section">
                            Section 2 content in the T-Pattern layout
                        </div>
                    </div>
                `,
                skeleton: `
                    <div class="t-pattern__header">
                        <div class="skeleton-text-group">
                            <div class="skeleton-text"></div>
                        </div>
                    </div>
                    <div class="t-pattern__content">
                        <div class="t-pattern__section">
                            <div class="skeleton-text-group">
                                <div class="skeleton-text"></div>
                                <div class="skeleton-text"></div>
                            </div>
                        </div>
                        <div class="t-pattern__section">
                            <div class="skeleton-text-group">
                                <div class="skeleton-text"></div>
                                <div class="skeleton-text"></div>
                            </div>
                        </div>
                    </div>
                `
            }
        };

        function toggleLoading() {
            isLoading = !isLoading;
            renderPattern();
        }

        function renderPattern() {
            // Z Pattern
            const zContainer = document.getElementById("z-content");
            zContainer.innerHTML = isLoading ? patterns.z.skeleton : patterns.z.real;

            // F Pattern
            const fContainer = document.getElementById("f-content");
            fContainer.innerHTML = isLoading ? patterns.f.skeleton : patterns.f.real;

            // T Pattern
            const tContainer = document.getElementById("t-content");
            tContainer.innerHTML = isLoading ? patterns.t.skeleton : patterns.t.real;
        }

        renderPattern(); // Initial render
