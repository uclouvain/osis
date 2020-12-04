CACHE_MAX_ELEMENTS = 10;

class BaseCache {
    constructor(context) {
        this.context = context;
        this.storageKey = BaseCache.getStorageKey(this.context, this.key);
    }

    getItem(key, defaultValue=null) {
        const storageKey = BaseCache.getStorageKey(this.context, key)
        const cachedData =  JSON.parse(localStorage.getItem(storageKey));
        if (cachedData === null && defaultValue !== null){
            return defaultValue;
        }
        return cachedData;
    }

    setItem(key, data) {
        const storageKey = BaseCache.getStorageKey(this.context, key)
        try{
            localStorage.setItem(storageKey, JSON.stringify(data));
        }catch {
            const eventExceed = new CustomEvent('cache_exceeded', {detail: this.context});
            document.dispatchEvent(eventExceed);
            localStorage.setItem(storageKey, JSON.stringify(data));
        }
        const eventGarbage = new CustomEvent('cache_garbage', {detail: this.context});
        document.dispatchEvent(eventGarbage);
    }

    removeItem(key){
        const storageKey = BaseCache.getStorageKey(this.context, key)
        localStorage.removeItem(storageKey);
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