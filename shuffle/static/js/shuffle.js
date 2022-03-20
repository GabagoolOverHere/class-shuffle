function data() {
    return {
        pickConfigShow: true,
        weekShow: false,
        uploadShow: false,
        result: false,
        mode: '',
        days: {
            'BOTH': {
                'FULL':
                    [{'Monday': {count: 0, weekday: 0}},
                        {'Tuesday': {count: 0, weekday: 1}},
                        {'Wednesday': {count: 0, weekday: 2}},
                        {'Thursday': {count: 0, weekday: 3}},
                        {'Friday': {count: 0, weekday: 4}}]
            },
            'GROUPS': {
                'A':
                    [{'Monday': {count: 0, weekday: 0}},
                        {'Tuesday': {count: 0, weekday: 1}},
                        {'Wednesday': {count: 0, weekday: 2}},
                        {'Thursday': {count: 0, weekday: 3}},
                        {'Friday': {count: 0, weekday: 4}}],
                'B':
                    [{'Monday': {count: 0, weekday: 0}},
                        {'Tuesday': {count: 0, weekday: 1}},
                        {'Wednesday': {count: 0, weekday: 2}},
                        {'Thursday': {count: 0, weekday: 3}},
                        {'Friday': {count: 0, weekday: 4}}]
            }
        }
    }
}