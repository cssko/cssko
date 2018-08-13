const React = window.React;
const Modifier = window.DraftJS.Modifier;
const EditorState = window.DraftJS.EditorState;

class KatexISource extends React.Component {
    componentDidMount() {
        const {editorState, entityType, onComplete} = this.props;

        const content = editorState.getCurrentContent();
        const selection = editorState.getSelection();
        const anchorKey = selection.getAnchorKey();
        const currentContent = editorState.getCurrentContent();
        const currentContentBlock = currentContent.getBlockForKey(anchorKey);
        const start = selection.getStartOffset();
        const end = selection.getEndOffset();
        const selectedText = currentContentBlock.getText().slice(start, end);

        // Uses the Draft.js API to create a new entity with the right data.
        const contentWithEntity = content.createEntity(entityType.type, 'IMMUTABLE', {
            content: selectedText,
        });
        const entityKey = contentWithEntity.getLastCreatedEntityKey();

        // We also add some text for the entity to be activated on.
        const text = `${selectedText}`;

        const newContent = Modifier.replaceText(content, selection, text, null, entityKey);
        const nextState = EditorState.push(editorState, newContent, 'insert-characters');

        onComplete(nextState);
    }

    render() {
        return null;
    }
}

const KatexIDecorator = (props) => {
    return React.createElement('span', {className: "katex-inline", style: {color: 'green'}}, props.children);
};

window.draftail.registerPlugin({
    type: 'KATEX_I',
    source: KatexISource,
    decorator: KatexIDecorator,
});

class KatexBSource extends React.Component {
    // TODO: These two classes have damn near everything pulled up
    componentDidMount() {
        const {editorState, entityType, onComplete} = this.props;

        const content = editorState.getCurrentContent();
        const selection = editorState.getSelection();
        const anchorKey = selection.getAnchorKey();
        const currentContent = editorState.getCurrentContent();
        const currentContentBlock = currentContent.getBlockForKey(anchorKey);
        const start = selection.getStartOffset();
        const end = selection.getEndOffset();
        const selectedText = currentContentBlock.getText().slice(start, end);

        // Uses the Draft.js API to create a new entity with the right data.
        const contentWithEntity = content.createEntity(entityType.type, 'IMMUTABLE', {
            content: selectedText,
        });
        const entityKey = contentWithEntity.getLastCreatedEntityKey();

        // We also add some text for the entity to be activated on.
        const text = `${selectedText}`;

        const newContent = Modifier.replaceText(content, selection, text, null, entityKey);
        const nextState = EditorState.push(editorState, newContent, 'insert-characters');

        onComplete(nextState);
    }

    render() {
        return null;
    }
}

const KatexBDecorator = (props) => {
    // const { entityKey, contentState } = props;
    // const data = contentState.getEntity(entityKey).getData();

    return React.createElement('span', {
        className: "katex-block",
        'style': {'display': 'block', 'text-align': 'center', 'margin': '1em 0', 'color': 'green'}
    }, props.children);
};

window.draftail.registerPlugin({
    type: 'KATEX_B',
    source: KatexBSource,
    decorator: KatexBDecorator,
});