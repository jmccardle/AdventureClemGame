""" Get episode data from clem log. Mainly for episodes that aren't recorded due to exceptions."""

log_file_path = "clembench.log"

# load log:
with open(log_file_path, 'r', encoding='utf-8') as log_file:
    clem_log = log_file.read()

# split lines:
clem_log_lines = clem_log.split("\n")[:-1]

# concatenate multiline entries:
log_entries: list = list()
for line_idx, line in enumerate(clem_log_lines):
    # print(line)
    if "INFO" in line or "ERROR" in line:
        # print(line)
        cur_entry = line
        # print(clem_log_lines[line_idx:])
        for following_line in clem_log_lines[line_idx+1:]:
            # print(following_line)
            if "INFO" in following_line or "ERROR" in following_line:
                break
            else:
                cur_entry += "\n" + following_line
        log_entries.append(cur_entry)
        # print()
    # if line_idx == 30:
    #    break

"""
for log_entry in log_entries:
    if "ERROR" in log_entry:
        print(log_entry)
"""

episode_starts: list = list()
for log_entry_idx, log_entry in enumerate(log_entries):
    if "Recording initial exploration state." in log_entry:
        episode_starts.append(log_entry_idx)

# print(episode_starts)

episode_spans: list = list()
for episode_start_idx, episode_start in enumerate(episode_starts[:-1]):
    episode_spans.append((episode_start, episode_starts[episode_start_idx+1]-1))
episode_spans.append((episode_starts[-1], len(log_entries)))

# print(episode_spans)

episode_action_counts: list = list()
for episode_span in episode_spans:
    cur_action_count: int = 0
    for log_entry in log_entries[episode_span[0]:episode_span[1]]:
        if "Cleaned action input" in log_entry:
            cur_action_count += 1
    episode_action_counts.append(cur_action_count)

print(episode_action_counts)

print(episode_action_counts.count(50))