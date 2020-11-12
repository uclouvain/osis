CACHE_MAX_ELEMENTS = 10;

class BaseCache {
    constructor(context, key) {
        this.context = context;
        this.key = key;
        this.storageKey = BaseCache.getStorageKey(this.context, this.key)
    }

    getItem(defaultValue=null) {
        const cachedData =  JSON.parse(localStorage.getItem(this.storageKey));
        if (cachedData === null && defaultValue !== null){
            return defaultValue;
        }
        return cachedData;
    }

    setItem(data) {
        try{
            localStorage.setItem(this.storageKey, JSON.stringify(data));
        }catch {
            const eventExceed = new CustomEvent('cache_exceeded', {detail: this.context});
            document.dispatchEvent(eventExceed);
            localStorage.setItem(this.storageKey, JSON.stringify(data));
        }
        const eventGarbage = new CustomEvent('cache_garbage', {detail: this.context});
        document.dispatchEvent(eventGarbage);
    }

    removeItem(){
        localStorage.removeItem(this.storageKey);
    }

    static getStorageKey(context, key) {
        return `${context}_${key}`;
    }

    static maxElements = CACHE_MAX_ELEMENTS;
    static garbageElements(context){
        const keys = Array.from(this.getKeys(context));
        if (keys.length > this.maxElements){
            localStorage.removeItem(keys[0]);
            localStorage.removeItem(keys[1]);
            localStorage.removeItem(keys[2]);
        }
    }

    static clear(context){
        const keys = Array.from(this.getKeys(context));
        for(const key of keys){
            localStorage.removeItem(key);
        }
    }

    static *getKeys(context){
        for (const key of this.getAllKeys()){
            if (key.startsWith(context)){
                yield key
            }
        }
    }

    static *getAllKeys(){
        var index = 0;
        var key = localStorage.key(index);
        while (key !== null){
            yield key;
            index += 1;
            key = localStorage.key(index);
        }
    }
}

document.addEventListener("cache_exceeded", function (e){
    BaseCache.clear(e.detail);
})

document.addEventListener("cache_garbage", function (e){
    BaseCache.garbageElements(e.detail);
})