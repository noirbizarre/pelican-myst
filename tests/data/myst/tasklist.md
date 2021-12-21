---
expected:
    disabled: |
        <ul>
        <li>[ ] unchecked</li>
        <li>[x] checked</li>
        </ul>
    default: |
        <ul class="contains-task-list">
        <li class="task-list-item"><input class="task-list-item-checkbox" disabled="disabled" type="checkbox"> unchecked</li>
        <li class="task-list-item"><input class="task-list-item-checkbox" checked="checked" disabled="disabled" type="checkbox"> checked</li>
        </ul>
    enabled: |
        <ul class="contains-task-list">
        <li class="task-list-item enabled"><input class="task-list-item-checkbox"  type="checkbox"> unchecked</li>
        <li class="task-list-item enabled"><input class="task-list-item-checkbox" checked="checked"  type="checkbox"> checked</li>
        </ul>
    label: |
        <ul class="contains-task-list">
        <li class="task-list-item"><label><input class="task-list-item-checkbox" disabled="disabled" type="checkbox"> unchecked</label></li>
        <li class="task-list-item"><label><input class="task-list-item-checkbox" checked="checked" disabled="disabled" type="checkbox"> checked</label></li>
        </ul>
---
- [ ] unchecked
- [x] checked
