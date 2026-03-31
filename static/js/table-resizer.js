/**
 * 表格列宽拖拽调整
 * 自动为页面中所有 .table-responsive > .table 添加列宽拖拽功能
 * 列宽会保存到 localStorage，刷新后自动恢复
 *
 * 导出列宽：
 *   - 快捷键 Ctrl+Shift+E：导出当前页面所有表格的列宽 CSS
 *   - 控制台调用 exportTableWidths()：同上
 *   - 拖拽后表格右上角出现"导出列宽"按钮
 */
(function() {
    'use strict';

    var managedTables = []; // { table, storageKey, index }

    // ========== 存储相关 ==========

    function getStorageKey(table, index) {
        var path = location.pathname.replace(/\/$/, '');
        var tableId = table.id || ('table-' + index);
        return 'col-widths:' + path + ':' + tableId;
    }

    function saveColumnWidths(table, storageKey) {
        var ths = table.querySelectorAll('thead > tr:last-child > th');
        var widths = [];
        ths.forEach(function(th) {
            widths.push(th.offsetWidth);
        });
        try {
            localStorage.setItem(storageKey, JSON.stringify(widths));
        } catch (e) {}
    }

    function restoreColumnWidths(table, storageKey) {
        try {
            var raw = localStorage.getItem(storageKey);
            if (!raw) return false;
            var widths = JSON.parse(raw);
            var ths = table.querySelectorAll('thead > tr:last-child > th');
            if (widths.length !== ths.length) return false;
            ths.forEach(function(th, i) {
                th.style.width = widths[i] + 'px';
            });
            return true;
        } catch (e) {
            return false;
        }
    }

    // ========== 拖拽逻辑 ==========

    function initTableResizer(table, index) {
        var headerRow = table.querySelector('thead > tr:last-child');
        if (!headerRow) return;

        var ths = headerRow.querySelectorAll('th');
        if (ths.length < 2) return;

        var storageKey = getStorageKey(table, index);
        managedTables.push({ table: table, storageKey: storageKey, index: index });

        table.style.tableLayout = 'fixed';

        var restored = restoreColumnWidths(table, storageKey);
        if (!restored) {
            ths.forEach(function(th) {
                th.style.width = th.offsetWidth + 'px';
            });
        }

        for (var i = 0; i < ths.length - 1; i++) {
            createResizeHandle(ths[i], table, storageKey);
        }
    }

    function createResizeHandle(th, table, storageKey) {
        th.style.position = 'relative';

        var handle = document.createElement('div');
        handle.className = 'col-resize-handle';
        th.appendChild(handle);

        var startX, startWidth, nextTh, startNextWidth;

        handle.addEventListener('mousedown', function(e) {
            e.preventDefault();
            e.stopPropagation();

            startX = e.pageX;
            startWidth = th.offsetWidth;
            nextTh = th.nextElementSibling;
            startNextWidth = nextTh ? nextTh.offsetWidth : 0;

            handle.classList.add('active');
            document.body.style.cursor = 'col-resize';
            document.body.style.userSelect = 'none';

            document.addEventListener('mousemove', onMouseMove);
            document.addEventListener('mouseup', onMouseUp);
        });

        function onMouseMove(e) {
            var diff = e.pageX - startX;
            var newWidth = startWidth + diff;
            var minWidth = 40;

            if (newWidth < minWidth) {
                diff = minWidth - startWidth;
                newWidth = minWidth;
            }

            if (nextTh) {
                var newNextWidth = startNextWidth - diff;
                if (newNextWidth < minWidth) {
                    newNextWidth = minWidth;
                    newWidth = startWidth + startNextWidth - minWidth;
                }
                nextTh.style.width = newNextWidth + 'px';
            }

            th.style.width = newWidth + 'px';
        }

        function onMouseUp() {
            handle.classList.remove('active');
            document.body.style.cursor = '';
            document.body.style.userSelect = '';

            document.removeEventListener('mousemove', onMouseMove);
            document.removeEventListener('mouseup', onMouseUp);

            saveColumnWidths(table, storageKey);
            showExportBtn(table);
        }
    }

    // ========== 导出列宽按钮 ==========

    function showExportBtn(table) {
        var wrapper = table.closest('.table-responsive') || table.parentElement;
        if (wrapper.querySelector('.col-export-btn')) return;

        var btn = document.createElement('button');
        btn.className = 'col-export-btn';
        btn.type = 'button';
        btn.innerHTML = '<i class="bi bi-clipboard-check"></i> 导出列宽CSS';
        btn.title = '将当前列宽导出为 CSS 代码（也可用 Ctrl+Shift+E）';
        wrapper.style.position = 'relative';
        wrapper.appendChild(btn);

        btn.addEventListener('click', function() {
            var css = generateCSSForTable(table);
            copyAndShow(css);
        });
    }

    // ========== CSS 生成 ==========

    function getTableSelector(table) {
        // 优先使用表格自身的特征 class（如 table-material-list）
        var classes = table.className.split(/\s+/);
        for (var i = 0; i < classes.length; i++) {
            var c = classes[i];
            if (c && c !== 'table' && c !== 'table-hover' && c !== 'table-sm' &&
                c !== 'mb-0' && c !== 'align-middle' && c !== 'table-bordered') {
                return '.' + c;
            }
        }
        // 无特征 class，使用 .table-responsive > .table
        return '.table-responsive > .table';
    }

    function getHeaderTexts(table) {
        var ths = table.querySelectorAll('thead > tr:last-child > th');
        var texts = [];
        ths.forEach(function(th) {
            var t = th.textContent.replace(/[\s*]+/g, '').trim();
            texts.push(t || '');
        });
        return texts;
    }

    function generateCSSForTable(table) {
        var selector = getTableSelector(table);
        var ths = table.querySelectorAll('thead > tr:last-child > th');
        var headers = getHeaderTexts(table);
        var lines = [];

        lines.push('/* 列宽设置 - ' + document.title + ' */');

        ths.forEach(function(th, i) {
            var w = th.offsetWidth;
            var comment = headers[i] ? '  /* ' + headers[i] + ' */' : '';
            var n = i + 1;
            var extraStyles = '';

            // 检测对齐方式
            var cs = window.getComputedStyle(th);
            if (cs.textAlign === 'right') {
                extraStyles += '\n    text-align: right;';
            } else if (cs.textAlign === 'center') {
                extraStyles += '\n    text-align: center;';
            }

            lines.push(
                selector + ' th:nth-child(' + n + '),' + comment + '\n' +
                selector + ' td:nth-child(' + n + ') {\n' +
                '    width: ' + w + 'px;\n' +
                '    min-width: ' + Math.round(w * 0.7) + 'px;' +
                extraStyles + '\n}'
            );
        });

        return lines.join('\n');
    }

    // ========== 导出全部表格 ==========

    function exportAll() {
        if (managedTables.length === 0) {
            showToast('当前页面没有可导出的表格');
            return '';
        }
        var parts = [];
        managedTables.forEach(function(item) {
            parts.push(generateCSSForTable(item.table));
        });
        var css = parts.join('\n\n');
        copyAndShow(css);
        return css;
    }

    // ========== 复制 & 提示 ==========

    function copyAndShow(css) {
        // 复制到剪贴板
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(css).then(function() {
                showToast('列宽 CSS 已复制到剪贴板，可直接粘贴到模板 <style> 中');
            }).catch(function() {
                showCSSModal(css);
            });
        } else {
            showCSSModal(css);
        }
        // 同时输出到控制台
        console.log('%c[表格列宽导出]', 'color:#3b82f6;font-weight:bold');
        console.log(css);
    }

    function showToast(msg) {
        var el = document.getElementById('colResizeToast');
        if (el) el.remove();

        el = document.createElement('div');
        el.id = 'colResizeToast';
        el.className = 'col-resize-toast';
        el.textContent = msg;
        document.body.appendChild(el);

        // 触发 reflow 后添加 show 类
        el.offsetHeight;
        el.classList.add('show');

        setTimeout(function() {
            el.classList.remove('show');
            setTimeout(function() { el.remove(); }, 300);
        }, 3000);
    }

    function showCSSModal(css) {
        // 如果剪贴板不可用，用模态框展示代码
        var overlay = document.createElement('div');
        overlay.className = 'col-resize-modal-overlay';
        overlay.innerHTML =
            '<div class="col-resize-modal">' +
            '  <div class="col-resize-modal-header">' +
            '    <strong>列宽 CSS 代码</strong>' +
            '    <button type="button" class="col-resize-modal-close">&times;</button>' +
            '  </div>' +
            '  <p class="text-muted small mb-2">复制以下代码，粘贴到对应模板的 &lt;style&gt; 块中即可</p>' +
            '  <textarea class="col-resize-modal-textarea" readonly>' + css.replace(/</g, '&lt;') + '</textarea>' +
            '  <button type="button" class="btn btn-sm btn-primary col-resize-modal-copy">全选复制</button>' +
            '</div>';
        document.body.appendChild(overlay);

        var textarea = overlay.querySelector('textarea');
        textarea.value = css; // 用 value 设置确保纯文本

        overlay.querySelector('.col-resize-modal-close').addEventListener('click', function() {
            overlay.remove();
        });
        overlay.querySelector('.col-resize-modal-copy').addEventListener('click', function() {
            textarea.select();
            document.execCommand('copy');
            this.textContent = '已复制';
            setTimeout(function() { overlay.remove(); }, 800);
        });
        overlay.addEventListener('click', function(e) {
            if (e.target === overlay) overlay.remove();
        });
    }

    // ========== 快捷键 & 全局接口 ==========

    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.shiftKey && e.key === 'E') {
            e.preventDefault();
            exportAll();
        }
    });

    window.exportTableWidths = exportAll;

    // ========== 初始化 ==========

    document.addEventListener('DOMContentLoaded', function() {
        var tables = document.querySelectorAll('.table-responsive > .table');
        tables.forEach(function(table, index) {
            initTableResizer(table, index);
        });
    });
})();
