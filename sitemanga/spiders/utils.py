def equalize_similar_dates(infos, threshold=1):
    for i, info in enumerate(infos):
        if i == len(infos) - 1:
            break
        td = infos[i + 1]['date'] - info['date']
        if td.days == 0 and td.seconds < threshold:
            # print((infos[i + 1]['date'] - info['date']))
            # print('{} - {}'.format(infos[i + 1]['date'], info['date']))
            infos[i + 1]['date'] = info['date']
    # exit()
    return infos