from jiratui.utils.history import HistoryEntry, HistoryManager


def test_add_to_history():
    # GIVEN
    manager = HistoryManager()
    item = HistoryEntry(key='key-1', item_type='task', status='completed', summary='summary')
    manager.add_work_item(item)
    # WHEN
    items = manager.get_history()
    # THEN
    assert items == [item]


def test_add_to_history_updates_existing():
    # GIVEN
    manager = HistoryManager()
    item_1 = HistoryEntry(key='key-1', item_type='task', status='completed', summary='summary 1')
    item_2 = HistoryEntry(key='key-2', item_type='epic', status='new', summary='summary 2')
    manager.add_work_item(item_1)
    manager.add_work_item(item_2)
    manager.add_work_item(item_1)
    # WHEN
    items = manager.get_history()
    # THEN
    assert items == [item_1, item_2]


def test_add_to_history_limit_reached():
    # GIVEN
    manager = HistoryManager()
    for i in range(20):
        manager.add_work_item(
            HistoryEntry(
                key=f'key-{i}', item_type='task', status='completed', summary=f'summary {i}'
            )
        )
    # WHEN
    manager.add_work_item(
        HistoryEntry(key='key-21', item_type='task', status='completed', summary='summary 21')
    )
    # THEN
    history = manager.get_history()
    assert len(history) == 20
    history_by_key = {x.key for x in history}
    assert 'key-21' in history_by_key
    assert 'key-0' not in history_by_key


def test_delete_work_item():
    # GIVEN
    manager = HistoryManager()
    item = HistoryEntry(key='key-1', item_type='task', status='completed', summary='summary')
    manager.add_work_item(item)
    # WHEN
    manager.delete_work_item('key-1')
    # THEN
    assert manager.get_history() == []


def test_empty_history():
    # GIVEN
    manager = HistoryManager()
    item = HistoryEntry(key='key-1', item_type='task', status='completed', summary='summary')
    manager.add_work_item(item)
    # WHEN
    manager.empty()
    # THEN
    assert manager.get_history() == []
